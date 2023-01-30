from nose.plugins.base import Plugin

from tiget.plugins import load_plugin


class NoseConfig(Plugin):
    def options(self, parser, env):
        pass

    def configure(self, options, conf):
        load_plugin('tiget.core')
