# -*- coding: utf-8 -*-
from easy_karabiner import util
from easy_karabiner.keymap import *


def test_keytokey():
    k = KeyToKey('ctrl', 'f12')
    s = '''
        <autogen> __KeyToKey__
            KeyCode::CONTROL_L,
            KeyCode::F12
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = KeyToKey('ctrl U', 'end shift_r home del del norepeat')
    s = '''
        <autogen> __KeyToKey__
            KeyCode::U, ModifierFlag::CONTROL_L, ModifierFlag::NONE,
            KeyCode::END, KeyCode::HOME, ModifierFlag::SHIFT_R,
            KeyCode::DELETE, KeyCode::DELETE, Option::NOREPEAT
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = KeyToKey('alt shift ,', 'fn left', has_modifier_none=False)
    s = '''
        <autogen> __KeyToKey__
            KeyCode::COMMA, ModifierFlag::OPTION_L, ModifierFlag::SHIFT_L,
            KeyCode::CURSOR_LEFT, ModifierFlag::FN
        </autogen>'''
    util.assert_xml_equal(k, s)

    options = ('DROPALLKEYS_DROP_KEY '
               'DROPALLKEYS_DROP_CONSUMERKEY '
               'DROPALLKEYS_DROP_POINTINGBUTTON')
    k = DropAllKeys('ModifierFlag::MY_VI_MODE', options)
    s = '''
        <autogen> __DropAllKeys__
            ModifierFlag::MY_VI_MODE,
            Option::DROPALLKEYS_DROP_KEY,
            Option::DROPALLKEYS_DROP_CONSUMERKEY,
            Option::DROPALLKEYS_DROP_POINTINGBUTTON
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = SimultaneousKeyPresses('9 0 9 shift', 'shift 0 left')
    s = '''
        <autogen> __SimultaneousKeyPresses__
          @begin
          KeyCode::KEY_9, KeyCode::KEY_0, KeyCode::KEY_9, ModifierFlag::SHIFT_L
          @end

          @begin
          KeyCode::KEY_0, ModifierFlag::SHIFT_L, KeyCode::CURSOR_LEFT
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

def test_keytomultikeys():
    k = DoublePressModifier('fn', 'cmd alt I')
    s = '''
        <autogen> __DoublePressModifier__
          KeyCode::FN,
          @begin
          KeyCode::FN
          @end
          @begin
          KeyCode::I, ModifierFlag::COMMAND_L, ModifierFlag::OPTION_L
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = DoublePressModifier('fn', 'F12', to_key='F11')
    s = '''
        <autogen> __DoublePressModifier__
          KeyCode::FN,
          @begin
          KeyCode::F11
          @end
          @begin
          KeyCode::F12
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = HoldingKeyToKey('esc', 'cmd_r ctrl_r alt_r shift_r')
    s = '''
        <autogen> __HoldingKeyToKey__
          KeyCode::ESCAPE,
          @begin
          KeyCode::ESCAPE
          @end
          @begin
          KeyCode::COMMAND_R, ModifierFlag::CONTROL_R, ModifierFlag::OPTION_R, ModifierFlag::SHIFT_R
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = KeyOverlaidModifier('caps', 'esc', 'ctrl')
    s = '''
        <autogen> __KeyOverlaidModifier__
          KeyCode::CAPSLOCK,
          @begin
          KeyCode::CONTROL_L
          @end
          @begin
          KeyCode::ESCAPE
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = KeyDownUpToKey('cmd ,', 'cmd shift left', 'cmd left')
    s = '''
        <autogen> __KeyDownUpToKey__
          KeyCode::COMMA, ModifierFlag::COMMAND_L, ModifierFlag::NONE,
          @begin
          KeyCode::CURSOR_LEFT, ModifierFlag::COMMAND_L, ModifierFlag::SHIFT_L
          @end
          @begin
          KeyCode::CURSOR_LEFT, ModifierFlag::COMMAND_L
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

def test_onekeyevent():
    k = BlockUntilKeyUp('sp')
    s = '''
        <autogen> __BlockUntilKeyUp__
          KeyCode::SPACE
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = DropKeyAfterRemap('mission_control MODIFIERFLAG_EITHER_LEFT_OR_RIGHT_SHIFT')
    s = '''
        <autogen> __DropKeyAfterRemap__
          KeyCode::MISSION_CONTROL,
          MODIFIERFLAG_EITHER_LEFT_OR_RIGHT_SHIFT
        </autogen>'''
    util.assert_xml_equal(k, s)

def test_zerokeyevent():
    k = PassThrough()
    s = '<autogen> __PassThrough__ </autogen>'
    util.assert_xml_equal(k, s)


def test_parse_keymap():
    k = parse_keymap('double', ['cmd K', 'up ' * 6])
    s = '''
        <autogen> __DoublePressModifier__
          KeyCode::K, ModifierFlag::COMMAND_L, ModifierFlag::NONE,

          @begin
          KeyCode::K, ModifierFlag::COMMAND_L
          @end

          @begin
          KeyCode::CURSOR_UP, KeyCode::CURSOR_UP, KeyCode::CURSOR_UP,
          KeyCode::CURSOR_UP, KeyCode::CURSOR_UP, KeyCode::CURSOR_UP
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = parse_keymap('__DoublePressModifier__', ['cmd J', 'down ' * 6])
    s = '''
        <autogen> __DoublePressModifier__
          KeyCode::J, ModifierFlag::COMMAND_L, ModifierFlag::NONE,

          @begin
          KeyCode::J, ModifierFlag::COMMAND_L
          @end

          @begin
          KeyCode::CURSOR_DOWN, KeyCode::CURSOR_DOWN, KeyCode::CURSOR_DOWN,
          KeyCode::CURSOR_DOWN, KeyCode::CURSOR_DOWN, KeyCode::CURSOR_DOWN
          @end
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = parse_keymap('KeyToKey', ['alt E', 'Open::FINDER'])
    s = '''
        <autogen> __KeyToKey__
            KeyCode::E, ModifierFlag::OPTION_L, ModifierFlag::NONE,
            KeyCode::VK_OPEN_URL_FINDER
        </autogen>'''
    util.assert_xml_equal(k, s)

    k = parse_keymap('__FlipScrollWheel__', ['FLIPSCROLLWHEEL_HORIZONTAL', 'FLIPSCROLLWHEEL_VERTICAL'])
    s = '''
        <autogen> __FlipScrollWheel__
          Option::FLIPSCROLLWHEEL_HORIZONTAL,
          Option::FLIPSCROLLWHEEL_VERTICAL
        </autogen>'''
    util.assert_xml_equal(k, s)