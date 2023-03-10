"""Common functionality for multiprocess system basees built with the
python 'multiprocess' module.  Intended as a base class, not for
direct usage."""


import logging
from thespian.actors import *
from thespian.system.systemBase import systemBase
from thespian.system.utilis import thesplog, checkActorCapabilities, partition
from thespian.system.transport import *
from thespian.system.logdirector import *
from thespian.system.utilis import setProcName, StatsManager
from thespian.system.addressManager import ActorLocalAddress
from thespian.system.messages.multiproc import *
from thespian.system.sourceLoader import loadModuleFromHashSource
from functools import partial
import multiprocessing
import signal
from datetime import timedelta


MAX_ADMIN_STARTUP_DELAY = timedelta(seconds=5)

uncatchable_signals = []
for sname in ['SIGCONT', 'SIGPIPE', 'SIGKILL', 'SIGSTOP']:
    try:
        uncatchable_signals.append(eval('signal.%s'%sname))
    except AttributeError:
        pass   # not defined for this OS
exit_signals = []
for sname in ['SIGTERM', 'SIGKILL', 'SIGQUIT', 'SIGABRT']:
    try:
        exit_signals.append(eval('signal.%s'%sname))
    except AttributeError:
        pass   # not defined for this OS
child_exit_signals = []
for sname in ['SIGCHLD']:
    try:
        child_exit_signals.append(eval('signal.%s'%sname))
    except AttributeError:
        pass   # not defined for this OS


def detach_child(childref):
    if hasattr(multiprocessing.process, '_children'):
        # Python 3.4
        multiprocessing.process._children.remove(childref)
    if hasattr(multiprocessing.process, '_current_process'):
        if hasattr(multiprocessing.process._current_process, '_children'):
            # Python 2.6
            multiprocessing.process._current_process._children.remove(childref)


class multiprocessCommon(systemBase):

    def __init__(self, system, logDefs = None):
        import sys, time
        system.capabilities['Python Version'] = tuple(sys.version_info)
        system.capabilities['Thespian Generation'] = ThespianGeneration
        system.capabilities['Thespian Version'] = str(int(time.time()*1000))

        self.transport = self.transportType(ExternalInterfaceTransportInit(),
                                            system.capabilities, logDefs)
        super(multiprocessCommon, self).__init__(system, logDefs)


    def _startAdmin(self, adminAddr, addrOfStarter, capabilities, logDefs):
        endpointPrep = self.transport.prepEndpoint(adminAddr, capabilities)

        multiprocessing.process._current_process._daemonic = False
        admin = multiprocessing.Process(target=startAdmin,
                                        args=(MultiProcAdmin,
                                              addrOfStarter,
                                              endpointPrep,
                                              self.transport.__class__,
                                              adminAddr,
                                              capabilities,
                                              logDefs),
                                        name='ThespianAdmin')
        admin.start()
        # admin must be explicity shutdown and is not automatically
        # stopped when this current process exits.
        detach_child(admin)

        self.transport.connectEndpoint(endpointPrep)

        response = self.transport.run(None, MAX_ADMIN_STARTUP_DELAY)
        if not response or not isinstance(response.message, EndpointConnected):
            raise InvalidActorAddress(adminAddr, 'not a valid ActorSystem admin')


def closeUnusedFiles(transport):
    import os, sys
    notouch = transport.protectedFileNumList()
    for each in [sys.stdin, sys.stderr, sys.stdout]:
        try:
            notouch.append(each.fileno())
        except AttributeError: pass
    for fdnum in range(3, 255):
        if fdnum not in notouch:
            try:
                os.close(fdnum)
            except OSError: pass


def closeFileNums(list):
    import os
    for fdnum in list:
        try:
            os.close(fdnum)
        except OSError: pass



from thespian.system.systemAdmin import ThespianAdmin

def startAdmin(adminClass, addrOfStarter, endpointPrep, transportClass,
               adminAddr, capabilities, logDefs):
    # Unix Daemonization; skipped if not available
    import os,sys
    if hasattr(os, 'setsid'):
        os.setsid()
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0,0))  # No core dumps
    except Exception: pass
    if hasattr(os, 'fork'):
        if os.fork(): sys.exit(0)

    # Slight trickiness here.  There may *already* be an admin bound
    # to this start address.  However, the external process attempting
    # to start is going to wait for the EndpointConnected message
    # before continuing, so ensure that message is *not* sent until
    # the local admin Transport has had time to bind and listen to the
    # local address, but also ensure that the message is *always* sent
    # even if the local admin could not start (caller will use
    # _verifyAdminRunning to ensure things are OK.
    transport = transportClass(endpointPrep)
    try:
        admin = adminClass(transport, adminAddr, capabilities, logDefs)
    except Exception:
        transport.scheduleTransmit(None,
                                   TransmitIntent(addrOfStarter, EndpointConnected(0)))
        raise
    # Send of EndpointConnected is deferred until the logger is setup.  See MultiProcReplicator.h_LoggerConnected below.

    admin.addrOfStarter = addrOfStarter
    setProcName(adminClass.__name__, admin.transport.myAddress)

    # Generate the "placeholder" loggerAddr directly instead of going
    # through the AddressManager because the logger is not managed as
    # a normal child.
    loggerAddr = ActorAddress(ActorLocalAddress(transport.myAddress, -1, None))
    admin.asLogger = None
    logAggregator = capabilities.get('Convention Address.IPv4', None)
    if logAggregator:
        try:
            logAggregator = transportClass.getAddressFromString(logAggregator)
        except Exception as ex:
            thesplog('Unable to adapt log aggregator address "%s" to a transport address: %s',
                     logAggregator, ex, level=logging.WARNING)
    admin.asLogProc = startASLogger(loggerAddr, logDefs, transport, capabilities,
                                    logAggregator
                                    if logAggregator != admin.transport.myAddress
                                    else None)
    #closeUnusedFiles(transport)
    admin.run()


class ChildInfo(object):
    def __init__(self, childAddr, childClass, childProc, childNum):
        self.childAddr = childAddr
        self.childClass = childClass
        self.childProc = childProc
        self.childNum  = childNum
    def __str__(self):
        return "Child #%s: %s @ %s (proc %s)"%(str(self.childNum),
                                               str(self.childClass),
                                               str(getattr(self, 'childRealAddr', self.childAddr)),
                                               str(self.childProc))


def startASLogger(loggerAddr, logDefs, transport, capabilities, aggregatorAddress=None):
    endpointPrep = transport.prepEndpoint(loggerAddr, capabilities)
    multiprocessing.process._current_process._daemonic = False
    logProc = multiprocessing.Process(target=startupASLogger,
                                      args = (transport.myAddress, endpointPrep,
                                              logDefs,
                                              transport.__class__, aggregatorAddress))
    logProc.daemon = True
    logProc.start()
    transport.connectEndpoint(endpointPrep)
    # When the caller that owns the transport starts their run(), it
    # will receive the LoggerConnected from the child to complete the
    # handshake and the sender will be the actual address of the
    # logger.
    return ChildInfo(loggerAddr, 'logger', logProc, endpointPrep.addrInst)



class MultiProcReplicator(object):

    def _startChildActor(self, childAddr, childClass, parentAddr, notifyAddr,
                         childRequirements=None,
                         sourceHash=None, sourceToLoad=None):
        """Create a new actor of type `childClass'.

           The `childAddr' is the local address of this child in the
           creator's address-space.

           The `parentAddr' is the parent of this actor in the
           heirarchy and will be another Actor or the local Admin.

           The `notifyAddr' is the Actor or Admin which should be
           notified on successful creation of this child Actor
           (normally this will be the parentAddr, but if the local
           Admin has been enlisted to create this Actor on behalf of
           another (possibly remote) Actor, the local Admin should be
           notified of the successful creation to complete it's
           administration and the Admin will forward the completion to
           the original requestor.).

           The optional `childRequirements' are a list of requirements
           dictated by the creating Actor.

        """
        if parentAddr is None:
            raise ActorSystemFailure('parentAddr cannot be None!')
        if self.asLogger is None:
            raise ActorSystemFailure('logger ADDR cannot be None!')

        if not checkActorCapabilities(childClass, self.capabilities, childRequirements,
                                      partial(loadModuleFromHashSource,
                                              sourceHash,
                                              { sourceHash: sourceToLoad })
                                      if sourceHash else None):
            raise NoCompatibleSystemForActor(childClass,
                                             "no system has compatible capabilities")

        # KWQ: when child starts it will have this parent address and it will initialize its transport and notify the parent, whereupon the parent will see the incoming message from the child with the id# indicated in the addressmanager localaddress and update the localaddress.  All this should happen in the transport though, not here.
        endpointPrep = self.transport.prepEndpoint(childAddr, self.capabilities)

        multiprocessing.process._current_process._daemonic = False

        # Ensure fileNumsToClose is a list, not an iterator because it
        # is an argument passed to the child.
        fileNumsToClose = list(self.transport.childResetFileNumList())

        child = multiprocessing.Process(target=startChild,  #KWQ: instantiates module specified by sourceHash to create actor
                                        args=(childClass,
                                              endpointPrep,
                                              self.transport.__class__,
                                              sourceHash or self._sourceHash,
                                              sourceToLoad,
                                              parentAddr,
                                              self._adminAddr,
                                              notifyAddr,
                                              self.asLogger,
                                              childRequirements,
                                              self.capabilities,
                                              fileNumsToClose),
                                        name='Actor_%s__%s'%(getattr(childClass, '__name__', childClass), str(childAddr)))
        child.start()
        # Also note that while non-daemonic children cause the current
        # process to automatically join() those children on exit,
        # daemonic children are sent a terminate() operation (usually
        # indicated by a SIGTERM under unix or TERMINATE indicator
        # under windows.  To avoid this, use another dirty trick and
        # remove all children from the _current_process._children list
        # so that they are not automatically stopped when this process
        # stops.
        detach_child(child)

        if not hasattr(self, '_child_procs'): self._child_procs = []
        self._child_procs.append(ChildInfo(childAddr, childClass, child, endpointPrep.addrInst))
        self.transport.connectEndpoint(endpointPrep)


    @staticmethod
    def _checkChildLiveness(childInfo):
        if not childInfo.childProc.is_alive():
            # Don't join forever; that might hang and it's ok to leave
            # zombies as long as we continue to make progress.
            childInfo.childProc.join(0.5)
            return False
        return True

    def _childExited(self, childAddr):
        self._child_procs = list(filter(self._checkChildLiveness, getattr(self, '_child_procs', [])))

    def childDied(self, signum, frame):
        # Signal handler for SIGCHLD; figure out which child and synthesize a ChildActorExited to handle it
        self._child_procs, dead = partition(self._checkChildLiveness,  getattr(self, '_child_procs', []))
        for each in dead:
            addr = getattr(each, 'childRealAddr', each.childAddr)
            self.transport.scheduleTransmit(None, TransmitIntent(self.transport.myAddress,
                                                                 ChildActorExited(addr)))

    def h_EndpointConnected(self, envelope):
        for C in getattr(self, '_child_procs', []):
            if envelope.message.childInstance == C.childNum:
                C.childRealAddr = envelope.sender
                break
        else:
            thesplog('Unknown child process endpoint connected: %s', envelope, level=logging.WARNING)
        self._pendingActorReady(envelope.message.childInstance, envelope.sender)
        return True

    def h_LoggerConnected(self, envelope):
        self.asLogger = envelope.sender
        # Dirty trick here to completely re-initialize logging in this
        # process... something the standard Python logging interface does
        # not allow via the API.
        self.oldLoggerRoot = logging.root
        logging.root = ThespianLogForwarder(self.asLogger, self.transport)
        logging.Logger.root = logging.root
        logging.Logger.manager = logging.Manager(logging.Logger.root)
        logging.getLogger('Thespian.Admin') \
               .info('ActorSystem Administrator startup @ %s', self.myAddress)

        # Now that logging is started, Admin startup can be confirmed
        self.transport.scheduleTransmit(None,
                                        TransmitIntent(self.addrOfStarter, EndpointConnected(0)))

        self._activate()
        return True


    def h_LogRecord(self, envelope):
        self._send_intent(TransmitIntent(self.asLogger, envelope.message))
        return True


    def _handleReplicatorMessages(self, envelope):
        if isinstance(envelope.message, EndpointConnected):
            return True, self.h_EndpointConnected(envelope)
        if isinstance(envelope.message, logging.LogRecord):
            return True, self.h_LogRecord(envelope)
        return False, True


    def _cleanupAdmin(self):
        if getattr(self, 'asLogger', None):
            if hasattr(self, 'oldLoggerRoot'):
                logging.root = self.oldLoggerRoot
                logging.Logger.root = self.oldLoggerRoot
                logging.Logger.manager = logging.Manager(logging.Logger.root)
            self.transport.run(TransmitOnly, maximumDuration=timedelta(milliseconds=250))
            import time
            time.sleep(0.05)  # allow children to exit and log their exit
            self.transport.scheduleTransmit(None, TransmitIntent(self.asLogger,
                                                                 LoggerExitRequest()))
            self.transport.run(TransmitOnly)
            if getattr(self, 'asLogProc', None):
                if self._checkChildLiveness(self.asLogProc):
                    import time
                    time.sleep(0.02)  # wait a little to allow logger to exit
                self._checkChildLiveness(self.asLogProc) # cleanup defunct proc



from thespian.system.actorManager import ActorManager

def signal_detector(name, addr):
    def signal_detected(signum, frame):
        thesplog('Actor %s @ %s got signal: %s', name, addr, signum,
                 level = logging.WARNING)
        # Simply exit; just by catching the signal the atexit handlers are enabled
        # if this signal is going to cause a process exit.
    return signal_detected


def shutdown_signal_detector(name, addr, am):
    def shutdown_signal_detected(signum, frame):
        thesplog('Actor %s @ %s got shutdown signal: %s', name, addr, signum,
                 level = logging.WARNING)
        am.transport.scheduleTransmit(None, TransmitIntent(am.transport.myAddress,
                                                           ActorExitRequest()))
    return shutdown_signal_detected


def startChild(childClass, endpoint, transportClass,
               sourceHash, sourceToLoad,
               parentAddr, adminAddr, notifyAddr, loggerAddr,
               childRequirements, currentSystemCapabilities,
               fileNumsToClose):

    closeFileNums(fileNumsToClose)

    # Dirty trick here to workaround multiprocessing trying to impose
    # an unnecessary restriction.  A process should be set daemonic
    # before start() if the parent shouldn't track it (an specifically
    # automatically join() the subprocess on exit).  For Actors, the
    # parent exists independently of the child and the ActorSystem
    # manages them, so daemonic processes are desired.  However,
    # multiprocessing imposes a restriction that daemonic processes
    # cannot create more processes.  The following reaches deep into
    # the implementation of the multiprocessing module to override
    # that restriction.  This process was already started as daemonic,
    # and it's detached from its parent.  The following simply clears
    # that flag locally so that other processes can be created from
    # this one.
    multiprocessing.process._current_process._daemonic = False

    transport = transportClass(endpoint)
    #closeUnusedFiles(transport)

    # Dirty trick here to completely re-initialize logging in this
    # process... something the standard Python logging interface does
    # not allow via the API.  We also do not want to run
    # logging.shutdown() because (a) that does not do enough to reset,
    # and (b) it shuts down handlers, but we want to leave the parent's
    # handlers alone.
    logging.root = ThespianLogForwarder(loggerAddr, transport)
    logging.Logger.root = logging.root
    logging.Logger.manager = logging.Manager(logging.Logger.root)

    logger = logging.getLogger('Thespian.ActorManager')

    am = MultiProcManager(childClass, transport,
                          sourceHash, sourceToLoad,
                          parentAddr, adminAddr,
                          childRequirements, currentSystemCapabilities)
    am.asLogger = loggerAddr
    am.transport.scheduleTransmit(None,
                                  TransmitIntent(notifyAddr,
                                                 EndpointConnected(endpoint.addrInst)))
    setProcName(getattr(childClass, '__name__', str(childClass)), am.transport.myAddress)

    sighandler = signal_detector(getattr(childClass, '__name__', str(childClass)),
                                 am.transport.myAddress)
    sigexithandler = shutdown_signal_detector(getattr(childClass, '__name__', str(childClass)),
                                              am.transport.myAddress,
                                              am)

    for each in range(1, signal.NSIG):
        # n.b. normally Python intercepts SIGINT to turn it into a
        # KeyboardInterrupt exception.  However, these Actors should
        # be detached from the keyboard, so revert to normal SIGINT
        # behavior.
        if each not in uncatchable_signals:
            if each in child_exit_signals:
                signal.signal(each, am.childDied)
                continue
            try:
                signal.signal(each,
                              sigexithandler if each in exit_signals else sighandler)
            except (RuntimeError,ValueError,EnvironmentError) as ex:
                # OK, this signal can't be caught for this
                # environment.  We did our best.
                pass

    am.run()



class MultiProcAdmin(MultiProcReplicator, ThespianAdmin): pass
class MultiProcManager(MultiProcReplicator, ActorManager): pass

