"""This test creates two top level actors and one sub-actor and
   verifies that the actors can exchange sequences of messages."""

import unittest
import time
import thespian.test.helpers
from thespian.actors import *
from thespian.test import ActorSystemTestCase

class rosaline(Actor):
    name = 'Rosaline'

class Romeo(Actor):
    def receiveMessage(self, msg, sender):
        if isinstance(msg, JulietAppears):
            self.send(msg.juliet, "But, soft! what light through yonder window breaks?")
        elif isinstance(msg, ActorExitRequest):
            pass  # nothing special, just die
        elif msg == 'Ay me!':
            self.send(sender, 'She speaks!')
        elif msg == 'O Romeo, Romeo! wherefore art thou Romeo?':
            self.send(sender, 'Shall I hear more, or shall I speak at this?')
        elif 'rose' in msg:
            pass # wait for it
        elif 'sweet' in msg:
            self.send(sender, 'Like softest music to attending ears!')
        elif 'hello' in msg:
            print('Hello from %s'%(str(self)))
        elif 'who_are_you' == msg:
            self.send(sender, self.myAddress)
        # otherwise sit and swoon


class Capulet(Actor):
    def receiveMessage(self, msg, sender):
        if msg == "has a daughter?":
            self.send(sender, self.createActor(Juliet))


class Juliet(Actor):
    def __init__(self, *args, **kw):
        self.nurse = None
        self.recalled = False
        super(Juliet, self).__init__(*args, **kw)
    def receiveMessage(self, msg, sender):
        if isinstance(msg, ActorExitRequest):
            pass  # nothing special, just die
        elif "what light" in msg:
            self.send(sender, 'Ay me!')
        elif msg == 'She speaks!':
            self.send(sender, 'O Romeo, Romeo! wherefore art thou Romeo?')
        elif msg == 'Shall I hear more, or shall I speak at this?':
            self.send(sender, "What's in a name? That which we call a rose")
            self.send(sender, "By any other name would smell as sweet")
        elif msg == 'Like softest music to attending ears!':
            if self.nurse:
                self.send(self.nurse, 'Anon, good nurse!')
            else:
                self.recalled = True
        elif msg == 'Mistress!':
            self.nurse = sender
            if self.recalled:
                self.send(self.nurse, 'Anon, good nurse!')
        elif 'who_are_you' == msg:
            self.send(sender, self.myAddress)


class Nurse(Actor):
    def __init__(self, *args, **kw):
        self.heardItAll = False
        super(Nurse, self).__init__(*args, **kw)
    def receiveMessage(self, msg, sender):
        if type(msg) == type((1,2)) and msg[0] == 'begin':
            self.send(msg[1], JulietAppears(msg[2]))
            self.send(msg[2], 'Mistress!')
        elif msg == 'Anon, good nurse!':
            self.heardItAll = True
        elif msg == 'done?':
            self.send(sender, 'Fini' if self.heardItAll else 'not yet')


class JulietAppears:
    stage = 'Right'
    def __init__(self, julietAddr):
        self.juliet = julietAddr


class TestASimpleSystem(ActorSystemTestCase):
    testbase='Simple'
    scope='func'

    def test01_ActorSystemStartupShutdown(self):
        rosalineA = ActorSystem().createActor(rosaline)
        # just finish, make sure no exception is thrown.

    def test01_1_ActorSystemMultipleShutdown(self):
        rosalineA = ActorSystem().createActor(rosaline)
        ActorSystem().shutdown()
        ActorSystem().shutdown()

    def test02_PrimaryActorCreation(self):
        romeo = ActorSystem().createActor(Romeo)
        juliet = ActorSystem().createActor(Juliet)
        self.assertNotEqual(romeo, juliet)

    def test03_CreateActorUniqueAddress(self):
        romeo = ActorSystem().createActor(Romeo)
        juliet = ActorSystem().createActor(Juliet)
        self.assertNotEqual(romeo, juliet)
        romeo2 = ActorSystem().createActor(Romeo)
        self.assertNotEqual(romeo, romeo2)

    def NOtest04_PossibleActorSystemResourceExhaustion(self):
        asys = ActorSystem()
        try:
            addresses = [asys.createActor(Juliet) for n in range(10000)]
        except OSError as err:
            import errno
            if err.errno == errno.EGAIN:
                pass
            else:
                raise


    def test05_ManyActorsUniqueAddress(self):
        asys = ActorSystem()
        addresses = [asys.createActor(Juliet) for n in range(100)]
        uniqueAddresses = set(addresses)
        if len(addresses) != len(uniqueAddresses):
            duplicates = [A for A in uniqueAddresses if len([X for X in addresses if X == A]) > 1]
            print('Duplicates: %s'%map(str, duplicates))
            if duplicates:
                for each in duplicates:
                    print('... %s at: %s'%(str(each), str([N for N,A in enumerate(addresses) if A == each])))
            print('Note: if this is a UDPTransport test, be advised that Linux occasionally does seem to assign the same UDP port multiple times.  Linux bug?')
        self.assertEqual(len(addresses), len(uniqueAddresses))

    def test06_ManyActorsValidAddresses(self):
        import string
        addresses = [ActorSystem().createActor(Juliet) for n in range(100)]
        for addr in addresses:
            invchar = ''.join([c for c in str(addr)
                               if c not in string.ascii_letters + string.digits + "-~/():., '|"])
            self.assertEqual(str(addr), str(addr) + invchar)  # invchar should be blank

    def test07_SingleNonListeningActorTell(self):
        rosalineA = ActorSystem().createActor(rosaline)
        # rosaline does not override the receiveMessage method, so the
        # Actor default method will throw an exception.  This will
        # Kill the rosaline Actor.  It's a top level Actor, so it will
        # not be restarted.  This will cause the 'hello' message to be
        # delivered to the DeadLetterBox.  Verify that no exception
        # makes its way out of the ActorSystem here.
        ActorSystem().tell(rosalineA, 'hello')
        self.assertTrue(True)

    def test08_SingleActorTell(self):
        romeoA = ActorSystem().createActor(Romeo)
        ActorSystem().tell(romeoA, 'hello')
        # Nothing much happens, Romeo is smitten and has no time for trivialities, but
        # he will try to generate str() of himself.

    def test09_SingleActorAsk(self):
        romeoA = ActorSystem().createActor(Romeo)
        resp = ActorSystem().ask(romeoA, 'O Romeo, Romeo! wherefore art thou Romeo?')
        self.assertEqual(resp, 'Shall I hear more, or shall I speak at this?')

    def test10_ActorAskWithNoResponse(self):
        romeoA = ActorSystem().createActor(Romeo)
        # This test is possibly unique to the simpleSystemBase, which
        # will run an process all messages on an ask (or tell) call.
        # Properly there is no way to determine if an answer is
        # forthcoming from an asynchronous system, so all this can do
        # is assert that there is no response within a particular time
        # period.  At this point, timing is not supported, so this
        # test is underspecified and assumptive.
        resp = ActorSystem().ask(romeoA, "What's in a name? That which we call a rose", 1.5)
        self.assertEqual(resp, None)
        # Now verify that the Actor and system are still alive and operating normally.
        resp = ActorSystem().ask(romeoA, 'O Romeo, Romeo! wherefore art thou Romeo?')
        self.assertEqual(resp, 'Shall I hear more, or shall I speak at this?')

    def test11_SingleActorAskMultipleTimes(self):
        romeoA = ActorSystem().createActor(Romeo)
        self.assertEqual(ActorSystem().ask(romeoA, 'O Romeo, Romeo! wherefore art thou Romeo?'),
                         'Shall I hear more, or shall I speak at this?')
        self.assertEqual(ActorSystem().ask(romeoA, 'O Romeo, Romeo! wherefore art thou Romeo?'),
                         'Shall I hear more, or shall I speak at this?')
        self.assertEqual(ActorSystem().ask(romeoA, 'Ay me!'), 'She speaks!')
        self.assertEqual(ActorSystem().ask(romeoA, 'O Romeo, Romeo! wherefore art thou Romeo?'),
                         'Shall I hear more, or shall I speak at this?')

    def test12_MultipleActorsAskMultipleTimes(self):
        play = ActorSystem()
        romeo = play.createActor(Romeo)
        self.assertEqual(play.ask(romeo, 'O Romeo, Romeo! wherefore art thou Romeo?'),
                         'Shall I hear more, or shall I speak at this?')
        juliet = play.createActor(Juliet)
        self.assertEqual(play.ask(romeo, 'O Romeo, Romeo! wherefore art thou Romeo?'),
                         'Shall I hear more, or shall I speak at this?')
        self.assertEqual(play.ask(romeo, 'Ay me!'), 'She speaks!')
        self.assertEqual(play.ask(juliet, 'She speaks!'),
                         'O Romeo, Romeo! wherefore art thou Romeo?')
        self.assertEqual(play.ask(romeo, 'Ay me!'), 'She speaks!')
        self.assertEqual(play.ask(juliet, "Do you know what light that is?"), 'Ay me!')

    def test13_SubActorCreation(self):
        capulet = ActorSystem().createActor(Capulet)
        juliet = ActorSystem().ask(capulet, 'has a daughter?', 2.5)
        print ('Juliet is: %s'%str(juliet))
        self.assertIsNot(juliet, None)
        if juliet:
            self.assertEqual(ActorSystem().ask(juliet, 'what light?'), 'Ay me!', 0.75)
            juliet2 = ActorSystem().ask(capulet, 'has a daughter?')
            self.assertIsNot(juliet2, None)
            if juliet2:
                self.assertEqual(ActorSystem().ask(juliet2, 'what light?'), 'Ay me!', 0.5)
            self.assertEqual(ActorSystem().ask(juliet, 'what light?'), 'Ay me!', 0.5)

    def test14_EntireActWithActorStart(self):
        play = ActorSystem()
        romeo = play.createActor(Romeo)
        juliet = play.createActor(Juliet)
        nurse = play.createActor(Nurse)
        self.assertEqual(play.ask(nurse, 'done?'), 'not yet')
        play.tell(nurse, ('begin', romeo, juliet))

        for X in range(50):
            if play.ask(nurse, 'done?') == 'Fini':
                break
            time.sleep(0.01)  # Allow some time for the entire act
        self.assertEqual(play.ask(nurse, 'done?'), 'Fini')

    def test15_IncompleteActMissingActor(self):
        play = ActorSystem()
        romeo = play.createActor(Romeo)
        juliet = play.createActor(Juliet)
        # no nurse actor created
        play.tell(romeo, JulietAppears(juliet))
        # No error should occur here when Juliet reaches the end and
        # doesn't have a nurse to tell.

        time.sleep(0.5)  # Allow some time for the entire act

        # Now create the nurse and tell her to talk to romeo and
        # juliet, which should cause completion
        nurse = play.createActor(Nurse)
        self.assertEqual(play.ask(nurse, 'done?'), 'not yet')
        play.tell(nurse, ('begin', romeo, juliet))

        for X in range(50):
            if play.ask(nurse, 'done?') == 'Fini':
                break
            time.sleep(0.01)  # Allow some time for the entire act
        self.assertEqual(play.ask(nurse, 'done?'), 'Fini')

    def test16_ActorProperties(self):
        play = ActorSystem()
        romeo = play.createActor(Romeo)
        juliet = play.createActor(Juliet)

        self.assertIsNotNone(play.ask(romeo, 'who_are_you', 0.25))
        self.assertIsNotNone(play.ask(juliet, 'who_are_you', 0.25))
        self.assertNotEqual(play.ask(romeo, 'who_are_you', 0.25),
                            play.ask(juliet, 'who_are_you', 0.25))


class TestMultiprocUDPSystem(TestASimpleSystem):
    testbase='MultiprocUDP'
    def setUp(self):
        self.setSystemBase('multiprocUDPBase')
        super(TestMultiprocUDPSystem, self).setUp()

class TestMultiprocTCPSystem(TestASimpleSystem):
    testbase='MultiprocTCP'
    def setUp(self):
        self.setSystemBase('multiprocTCPBase')
        super(TestMultiprocTCPSystem, self).setUp()

class TestMultiprocQueueSystem(TestASimpleSystem):
    testbase='MultiprocQueue'
    def setUp(self):
        self.setSystemBase('multiprocQueueBase')
        super(TestMultiprocQueueSystem, self).setUp()

