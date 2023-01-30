from framework.dependency_management.dependency_resolver import ServiceLocator
"""
Plugin for probing HTTP Rpc
"""

DESCRIPTION = " HTTP Rpc Probing "

def run(PluginInfo):
    #ServiceLocator.get_component("config").Show()
    #print "Content="+Content
    return ServiceLocator.get_component("plugin_helper").CommandDump('Test Command', 'Output', ServiceLocator.get_component("resource").GetResources('HttpRpcProbeMethods'), PluginInfo, []) # No previous output
