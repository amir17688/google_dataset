##########################################################################
#
#  Copyright (c) 2014-2015, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import stat
import shutil
import unittest

import IECore

import Gaffer
import GafferTest
import GafferDispatch
import GafferDispatchTest

class LocalDispatcherTest( GafferTest.TestCase ) :

	def setUp( self ) :

		GafferTest.TestCase.setUp( self )

		if not "LocalTest" in GafferDispatch.Dispatcher.registeredDispatchers():

			def create() :
				dispatcher = GafferDispatch.Dispatcher.create( "Local" )
				dispatcher["jobsDirectory"].setValue( "/tmp/dispatcherTest" )
				return dispatcher

			GafferDispatch.Dispatcher.registerDispatcher( "LocalTest", create )

	def testDispatcherRegistration( self ) :

		self.failUnless( "Local" in GafferDispatch.Dispatcher.registeredDispatchers() )
		self.failUnless( GafferDispatch.Dispatcher.create( "Local" ).isInstanceOf( GafferDispatch.LocalDispatcher.staticTypeId() ) )

	def testDispatch( self ) :

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		fileName = "/tmp/dispatcherTest/result.txt"

		def createWriter( text ) :
			node = GafferDispatchTest.TextWriter()
			node["mode"].setValue( "a" )
			node["fileName"].setValue( fileName )
			node["text"].setValue( text + " on ${frame};" )
			return node

		# Create a tree of dependencies for execution:
		# n1 requires:
		# - n2 requires:
		#    -n2a
		#    -n2b
		s = Gaffer.ScriptNode()
		s["n1"] = createWriter( "n1" )
		s["n2"] = createWriter( "n2" )
		s["n2a"] = createWriter( "n2a" )
		s["n2b"] = createWriter( "n2b" )
		s["n1"]["preTasks"][0].setInput( s["n2"]["task"] )
		s["n2"]["preTasks"][0].setInput( s["n2a"]["task"] )
		s["n2"]["preTasks"][1].setInput( s["n2b"]["task"] )

		# No files should exist yet
		self.assertEqual( os.path.isfile( fileName ), False )

		# Executing n1 should trigger execution of all of them
		dispatcher.dispatch( [ s["n1"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = s.context().substitute( "n2a on ${frame};n2b on ${frame};n2 on ${frame};n1 on ${frame};" )
		self.assertEqual( text, expectedText )

		# Executing n1 and anything else, should be the same as just n1, but forcing n2b execution puts it before n2a
		os.remove( fileName )
		dispatcher.dispatch( [ s["n2b"], s["n1"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = s.context().substitute( "n2b on ${frame};n2a on ${frame};n2 on ${frame};n1 on ${frame};" )
		self.assertEqual( text, expectedText )

		# Executing all nodes should be the same as just n1
		os.remove( fileName )
		dispatcher.dispatch( [ s["n2"], s["n2b"], s["n1"], s["n2a"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = s.context().substitute( "n2a on ${frame};n2b on ${frame};n2 on ${frame};n1 on ${frame};" )
		self.assertEqual( text, expectedText )

		# Executing a sub-branch (n2) should only trigger execution in that branch
		os.remove( fileName )
		dispatcher.dispatch( [ s["n2"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = s.context().substitute( "n2a on ${frame};n2b on ${frame};n2 on ${frame};" )
		self.assertEqual( text, expectedText )

		# Executing a leaf node, should not trigger other executions.
		os.remove( fileName )
		dispatcher.dispatch( [ s["n2b"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = s.context().substitute( "n2b on ${frame};" )
		self.assertEqual( text, expectedText )

	def testDispatchDifferentFrame( self ) :

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		context = Gaffer.Context( s.context() )
		context.setFrame( s.context().getFrame() + 10 )

		with context :
			GafferDispatch.Dispatcher.create( "LocalTest" ).dispatch( [ s["n1"] ] )

		fileName = context.substitute( s["n1"]["fileName"].getValue() )
		self.assertTrue( os.path.isfile( fileName ) )
		with file( fileName, "r" ) as f :
			text = f.read()
		self.assertEqual( text, "%s on %d" % ( s["n1"].getName(), context.getFrame() ) )

	def testDispatchFullRange( self ) :

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["framesMode"].setValue( GafferDispatch.Dispatcher.FramesMode.FullRange )
		frameList = IECore.FrameList.parse( "5-7" )
		fileName = "/tmp/dispatcherTest/result.txt"

		def createWriter( text ) :
			node = GafferDispatchTest.TextWriter()
			node["mode"].setValue( "a" )
			node["fileName"].setValue( fileName )
			node["text"].setValue( text + " on ${frame};" )
			return node

		# Create a tree of dependencies for execution:
		# n1 requires:
		# - n2 requires:
		#    -n2a
		#    -n2b
		s = Gaffer.ScriptNode()
		s["frameRange"]["start"].setValue( 5 )
		s["frameRange"]["end"].setValue( 7 )
		s["n1"] = createWriter( "n1" )
		s["n2"] = createWriter( "n2" )
		s["n2a"] = createWriter( "n2a" )
		s["n2b"] = createWriter( "n2b" )
		s["n1"]["preTasks"][0].setInput( s["n2"]["task"] )
		s["n2"]["preTasks"][0].setInput( s["n2a"]["task"] )
		s["n2"]["preTasks"][1].setInput( s["n2b"]["task"] )

		# No files should exist yet
		self.assertEqual( os.path.isfile( fileName ), False )

		# Executing n1 should trigger execution of all of them
		dispatcher.dispatch( [ s["n1"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = ""
		for frame in frameList.asList() :
			context = Gaffer.Context( s.context() )
			context.setFrame( frame )
			expectedText += context.substitute( "n2a on ${frame};n2b on ${frame};n2 on ${frame};n1 on ${frame};" )
		self.assertEqual( text, expectedText )

		# Executing a leaf node, should not trigger other executions.
		os.remove( fileName )
		dispatcher.dispatch( [ s["n2b"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = ""
		for frame in frameList.asList() :
			context = Gaffer.Context( s.context() )
			context.setFrame( frame )
			expectedText += context.substitute( "n2b on ${frame};" )
		self.assertEqual( text, expectedText )

	def testDispatchCustomRange( self ) :

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["framesMode"].setValue( GafferDispatch.Dispatcher.FramesMode.CustomRange )
		frameList = IECore.FrameList.parse( "2-6x2" )
		dispatcher["frameRange"].setValue( str(frameList) )
		fileName = "/tmp/dispatcherTest/result.txt"

		def createWriter( text ) :
			node = GafferDispatchTest.TextWriter()
			node["mode"].setValue( "a" )
			node["fileName"].setValue( fileName )
			node["text"].setValue( text + " on ${frame};" )
			return node

		# Create a tree of dependencies for execution:
		# n1 requires:
		# - n2 requires:
		#    -n2a
		#    -n2b
		s = Gaffer.ScriptNode()
		s["n1"] = createWriter( "n1" )
		s["n2"] = createWriter( "n2" )
		s["n2a"] = createWriter( "n2a" )
		s["n2b"] = createWriter( "n2b" )
		s["n1"]["preTasks"][0].setInput( s["n2"]["task"] )
		s["n2"]["preTasks"][0].setInput( s["n2a"]["task"] )
		s["n2"]["preTasks"][1].setInput( s["n2b"]["task"] )

		# No files should exist yet
		self.assertEqual( os.path.isfile( fileName ), False )

		# Executing n1 should trigger execution of all of them
		dispatcher.dispatch( [ s["n1"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = ""
		for frame in frameList.asList() :
			context = Gaffer.Context( s.context() )
			context.setFrame( frame )
			expectedText += context.substitute( "n2a on ${frame};n2b on ${frame};n2 on ${frame};n1 on ${frame};" )
		self.assertEqual( text, expectedText )

		# Executing a leaf node, should not trigger other executions.
		os.remove( fileName )
		dispatcher.dispatch( [ s["n2b"] ] )
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = ""
		for frame in frameList.asList() :
			context = Gaffer.Context( s.context() )
			context.setFrame( frame )
			expectedText += context.substitute( "n2b on ${frame};" )
		self.assertEqual( text, expectedText )

	def testDispatchBadCustomRange( self ) :

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["framesMode"].setValue( GafferDispatch.Dispatcher.FramesMode.CustomRange )
		dispatcher["frameRange"].setValue( "notAFrameRange" )

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		self.assertRaises( RuntimeError, dispatcher.dispatch, [ s["n1"] ] )
		self.assertFalse( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

	def testContextVariation( self ) :

		s = Gaffer.ScriptNode()
		context = Gaffer.Context( s.context() )
		context["script:name"] = "notTheRealScriptName"
		context["textWriter:replace"] = IECore.StringVectorData( [ " ", "\n" ] )

		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/${script:name}_####.txt" )
		s["n1"]["text"].setValue( "${script:name} on ${frame}" )

		fileName = context.substitute( s["n1"]["fileName"].getValue() )
		self.assertFalse( os.path.isfile( fileName ) )

		with context :
			GafferDispatch.Dispatcher.create( "LocalTest" ).dispatch( [ s["n1"] ] )

		self.assertTrue( os.path.isfile( fileName ) )
		self.assertTrue( os.path.basename( fileName ).startswith( context["script:name"] ) )
		with file( fileName, "r" ) as f :
			text = f.read()
		expected = "%s on %d" % ( context["script:name"], context.getFrame() )
		expected = expected.replace( context["textWriter:replace"][0], context["textWriter:replace"][1] )
		self.assertEqual( text, expected )

	def testDispatcherSignals( self ) :

		class CapturingSlot2( list ) :

			def __init__( self, *signals ) :

				self.__connections = []
				for s in signals :
					self.__connections.append( s.connect( Gaffer.WeakMethod( self.__slot ) ) )

			def __slot( self, d, nodes ) :
				self.append( (d,nodes) )

		preCs = CapturingSlot2( GafferDispatch.Dispatcher.preDispatchSignal() )
		self.assertEqual( len( preCs ), 0 )
		postCs = GafferTest.CapturingSlot( GafferDispatch.Dispatcher.postDispatchSignal() )
		self.assertEqual( len( postCs ), 0 )

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher.dispatch( [ s["n1"] ] )

		self.assertEqual( len( preCs ), 1 )
		self.failUnless( preCs[0][0].isSame( dispatcher ) )
		self.assertEqual( preCs[0][1], [ s["n1"] ] )

		self.assertEqual( len( postCs ), 1 )
		self.failUnless( postCs[0][0].isSame( dispatcher ) )
		self.assertEqual( postCs[0][1], [ s["n1"] ] )

	def testExecuteInBackground( self ) :

		preCs = GafferTest.CapturingSlot( GafferDispatch.LocalDispatcher.preDispatchSignal() )
		self.assertEqual( len( preCs ), 0 )
		postCs = GafferTest.CapturingSlot( GafferDispatch.LocalDispatcher.postDispatchSignal() )
		self.assertEqual( len( postCs ), 0 )

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )
		dispatcher.dispatch( [ s["n1"] ] )

		# the dispatching started and finished
		self.assertEqual( len( preCs ), 1 )
		self.assertEqual( len( postCs ), 1 )

		# but the execution hasn't finished yet
		self.assertFalse( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

		# wait long enough to finish execution
		self.assertEqual( len(dispatcher.jobPool().jobs()), 1 )
		dispatcher.jobPool().waitForAll()
		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )

		self.assertTrue( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

	def testMixedImmediateAndBackground( self ) :

		preCs = GafferTest.CapturingSlot( GafferDispatch.LocalDispatcher.preDispatchSignal() )
		self.assertEqual( len( preCs ), 0 )
		postCs = GafferTest.CapturingSlot( GafferDispatch.LocalDispatcher.postDispatchSignal() )
		self.assertEqual( len( postCs ), 0 )

		fileName = "/tmp/dispatcherTest/result.txt"

		def createWriter( text ) :
			node = GafferDispatchTest.TextWriter()
			node["mode"].setValue( "a" )
			node["fileName"].setValue( fileName )
			node["text"].setValue( text + " on ${frame};" )
			return node

		s = Gaffer.ScriptNode()
		# Create a tree of dependencies for execution:
		# n1 requires:
		# - n2 requires:
		#    -n2a
		#    -n2b
		# - n3
		s = Gaffer.ScriptNode()
		s["n1"] = createWriter( "n1" )
		s["n2"] = createWriter( "n2" )
		# force the entire n2 tree to execute in the foreground
		s["n2"]["dispatcher"]["immediate"].setValue( True )
		s["n2a"] = createWriter( "n2a" )
		s["n2b"] = createWriter( "n2b" )
		s["n3"] = createWriter( "n3" )
		s["n1"]["preTasks"][0].setInput( s["n2"]["task"] )
		s["n1"]["preTasks"][1].setInput( s["n3"]["task"] )
		s["n2"]["preTasks"][0].setInput( s["n2a"]["task"] )
		s["n2"]["preTasks"][1].setInput( s["n2b"]["task"] )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )
		dispatcher["framesMode"].setValue( GafferDispatch.Dispatcher.FramesMode.CustomRange )
		frameList = IECore.FrameList.parse( "2-6x2" )
		dispatcher["frameRange"].setValue( str(frameList) )

		dispatcher.dispatch( [ s["n1"] ] )

		# the dispatching started and finished
		self.assertEqual( len( preCs ), 1 )
		self.assertEqual( len( postCs ), 1 )

		# all the foreground execution has finished
		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		expectedText = ""
		for frame in frameList.asList() :
			context = Gaffer.Context( s.context() )
			context.setFrame( frame )
			expectedText += context.substitute( "n2a on ${frame};n2b on ${frame};n2 on ${frame};" )
		self.assertEqual( text, expectedText )

		# wait long enough for background execution to finish
		self.assertEqual( len(dispatcher.jobPool().jobs()), 1 )
		dispatcher.jobPool().waitForAll()
		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )

		self.assertEqual( os.path.isfile( fileName ), True )
		with file( fileName, "r" ) as f :
			text = f.read()
		# don't reset the expectedText since we're still appending
		for frame in frameList.asList() :
			context = Gaffer.Context( s.context() )
			context.setFrame( frame )
			expectedText += context.substitute( "n3 on ${frame};n1 on ${frame};" )
		self.assertEqual( text, expectedText )

	def testMultipleDispatchers( self ) :

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )
		dispatcher2 = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher2["executeInBackground"].setValue( True )
		dispatcher.dispatch( [ s["n1"] ] )
		c = s.context()
		c.setFrame( 2 )
		with c :
			dispatcher2.dispatch( [ s["n1"] ] )

		# wait long enough for background execution to finish
		self.assertEqual( len(dispatcher.jobPool().jobs()), 2 )
		dispatcher.jobPool().waitForAll()
		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )

		self.assertTrue( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )
		self.assertTrue( os.path.isfile( c.substitute( s["n1"]["fileName"].getValue() ) ) )

	def testFailure( self ) :

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )
		s["n2"] = GafferDispatchTest.TextWriter()
		s["n2"]["fileName"].setValue( "" )
		s["n2"]["text"].setValue( "n2 on ${frame}" )
		s["n3"] = GafferDispatchTest.TextWriter()
		s["n3"]["fileName"].setValue( "/tmp/dispatcherTest/n3_####.txt" )
		s["n3"]["text"].setValue( "n3 on ${frame}" )
		s["n1"]["preTasks"][0].setInput( s["n2"]["task"] )
		s["n2"]["preTasks"][0].setInput( s["n3"]["task"] )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher.dispatch( [ s["n1"] ] )

		# it still cleans up the JobPool
		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )

		# n3 executed correctly
		self.assertTrue( os.path.isfile( s.context().substitute( s["n3"]["fileName"].getValue() ) ) )
		with file( s.context().substitute( s["n3"]["fileName"].getValue() ), "r" ) as f :
			text = f.read()
		self.assertEqual( text, "n3 on %d" % s.context().getFrame() )

		# n2 failed, so n1 never executed
		self.assertFalse( os.path.isfile( s.context().substitute( s["n2"]["fileName"].getValue() ) ) )
		self.assertFalse( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

		self.tearDown()

		dispatcher["executeInBackground"].setValue( True )
		dispatcher.dispatch( [ s["n1"] ] )

		# wait long enough for background execution to finish
		self.assertEqual( len(dispatcher.jobPool().jobs()), 1 )
		dispatcher.jobPool().waitForAll()
		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )

		# n3 executed correctly
		self.assertTrue( os.path.isfile( s.context().substitute( s["n3"]["fileName"].getValue() ) ) )
		with file( s.context().substitute( s["n3"]["fileName"].getValue() ), "r" ) as f :
			text = f.read()
		self.assertEqual( text, "n3 on %d" % s.context().getFrame() )

		# n2 failed, so n1 never executed
		self.assertFalse( os.path.isfile( s.context().substitute( s["n2"]["fileName"].getValue() ) ) )
		self.assertFalse( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

	def testKill( self ) :

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/n1_####.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )

		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )
		dispatcher.dispatch( [ s["n1"] ] )
		self.assertEqual( len(dispatcher.jobPool().jobs()), 1 )

		# the execution hasn't finished yet
		self.assertFalse( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

		# kill the job
		dispatcher.jobPool().jobs()[0].kill()

		# wait long enough for the process to die
		dispatcher.jobPool().waitForAll()
		self.assertEqual( len(dispatcher.jobPool().jobs()), 0 )

		# make sure it never wrote the file
		self.assertFalse( os.path.isfile( s.context().substitute( s["n1"]["fileName"].getValue() ) ) )

	def testSpacesInContext( self ) :

		s = Gaffer.ScriptNode()

		s["n"] = GafferDispatchTest.TextWriter()
		s["n"]["fileName"].setValue( "/tmp/dispatcherTest/test.txt" )
		s["n"]["text"].setValue( "${test}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )

		c = Gaffer.Context()
		c["test"] = "i am a string with spaces"

		with c :
			dispatcher.dispatch( [ s["n"] ] )

		dispatcher.jobPool().waitForAll()

		text = "".join( open( "/tmp/dispatcherTest/test.txt" ).readlines() )
		self.assertEqual( text, "i am a string with spaces" )

	def testUIContextEntriesIgnored( self ) :

		s = Gaffer.ScriptNode()
		s["n"] = GafferDispatchTest.TextWriter()
		s["n"]["fileName"].setValue( "/tmp/dispatcherTest/out.txt" )
		s["n"]["text"].setValue( "${foo} ${ui:foo}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )

		c = Gaffer.Context()
		c["ui:foo"] = "uiFoo"
		c["foo"] = "foo"

		with c :
			dispatcher.dispatch( [ s["n"] ] )

		dispatcher.jobPool().waitForAll()

		text = "".join( open( "/tmp/dispatcherTest/out.txt" ).readlines() )
		self.assertEqual( text, "foo " )

	def testContextLockedDuringBackgroundDispatch( self ) :

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/out.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame} with ${foo}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )

		c = Gaffer.Context( s.context() )
		c["foo"] = "foo"

		with c :
			dispatcher.dispatch( [ s["n1"] ] )

		self.assertFalse( os.path.isfile( "/tmp/dispatcherTest/out.txt" ) )

		foo = s["variables"].addMember( "foo", IECore.StringData( "foo" ) )

		dispatcher.jobPool().waitForAll()

		self.assertTrue( os.path.isfile( "/tmp/dispatcherTest/out.txt" ) )

		text = "".join( open( "/tmp/dispatcherTest/out.txt" ).readlines() )
		self.assertEqual( text, "n1 on 1 with foo" )

	def testNodeNamesLockedDuringBackgroundDispatch( self ) :

		s = Gaffer.ScriptNode()
		s["n1"] = GafferDispatchTest.TextWriter()
		s["n1"]["fileName"].setValue( "/tmp/dispatcherTest/out.txt" )
		s["n1"]["text"].setValue( "n1 on ${frame}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )
		dispatcher.dispatch( [ s["n1"] ] )

		self.assertFalse( os.path.isfile( "/tmp/dispatcherTest/out.txt" ) )

		s["n1"].setName( "n2" )

		dispatcher.jobPool().waitForAll()

		self.assertTrue( os.path.isfile( "/tmp/dispatcherTest/out.txt" ) )

		text = "".join( open( "/tmp/dispatcherTest/out.txt" ).readlines() )
		self.assertEqual( text, "n1 on 1" )

	def testIgnoreScriptLoadErrors( self ) :

		s = Gaffer.ScriptNode()
		s["n"] = GafferDispatchTest.TextWriter()
		s["n"]["fileName"].setValue( "/tmp/dispatcherTest/scriptLoadErrorTest.txt" )
		s["n"]["text"].setValue( "test" )

		# because this doesn't have the dynamic flag set,
		# it won't serialise/load properly.
		s["n"]["user"]["badPlug"] = Gaffer.IntPlug()
		s["n"]["user"]["badPlug"].setValue( 10 )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )

		dispatcher.dispatch( [ s["n"] ] )
		dispatcher.jobPool().waitForAll()

		self.assertFalse( os.path.isfile( "/tmp/dispatcherTest/scriptLoadErrorTest.txt" ) )

		dispatcher["ignoreScriptLoadErrors"].setValue( True )
		dispatcher.dispatch( [ s["n"] ] )
		dispatcher.jobPool().waitForAll()

		self.assertTrue( os.path.isfile( "/tmp/dispatcherTest/scriptLoadErrorTest.txt" ) )

	def testBackgroundBatchesCanAccessJobDirectory( self ) :

		s = Gaffer.ScriptNode()

		s["w"] = GafferDispatchTest.TextWriter()
		s["w"]["fileName"].setValue( "${dispatcher:jobDirectory}/test.####.txt" )
		s["w"]["text"].setValue( "w on ${frame} from ${dispatcher:jobDirectory}" )

		dispatcher = GafferDispatch.Dispatcher.create( "LocalTest" )
		dispatcher["executeInBackground"].setValue( True )
		dispatcher["framesMode"].setValue( GafferDispatch.Dispatcher.FramesMode.CustomRange )
		frameList = IECore.FrameList.parse( "2-6x2" )
		dispatcher["frameRange"].setValue( str(frameList) )
		dispatcher.dispatch( [ s["w"] ] )
		dispatcher.jobPool().waitForAll()

		# a single dispatch should have the same job directory for all batches
		jobDir = dispatcher.jobDirectory()
		self.assertEqual( next( open( "%s/test.0002.txt" % jobDir ) ), "w on 2 from %s" % jobDir )
		self.assertEqual( next( open( "%s/test.0004.txt" % jobDir ) ), "w on 4 from %s" % jobDir )
		self.assertEqual( next( open( "%s/test.0006.txt" % jobDir ) ), "w on 6 from %s" % jobDir )

	def tearDown( self ) :

		GafferTest.TestCase.tearDown( self )

		shutil.rmtree( "/tmp/dispatcherTest", ignore_errors = True )

if __name__ == "__main__":
	unittest.main()
