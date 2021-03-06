# -*- coding: utf-8 -*-
from django.utils.six.moves import zip


def copy_plugins_to(old_plugins, to_placeholder,
                    to_language=None, parent_plugin_id=None, no_signals=False):
    """
    Copies a list of plugins to a placeholder to a language.
    """
    # TODO: Refactor this and copy_plugins to cleanly separate plugin tree/node
    # copying and remove the need for the mutating parameter old_parent_cache.
    old_parent_cache = {}
    # For subplugin copy, first plugin's parent must be nulled before copying.
    if old_plugins:
        old_plugins[0].parent = old_plugins[0].parent_id = None
    new_plugins = [old.copy_plugin(to_placeholder, to_language or old.language,
                                   old_parent_cache, no_signals)
                   for old in old_plugins]
    if new_plugins and parent_plugin_id:
        from cms.models import CMSPlugin
        new_plugins[0].parent_id = parent_plugin_id
        new_plugins[0].save()
        new_plugins[0].move(CMSPlugin.objects.get(pk=parent_plugin_id), pos='last-child')
        new_plugins[0] = CMSPlugin.objects.get(pk=new_plugins[0].pk)
    plugins_ziplist = list(zip(new_plugins, old_plugins))

    # this magic is needed for advanced plugins like Text Plugins that can have
    # nested plugins and need to update their content based on the new plugins.
    for new_plugin, old_plugin in plugins_ziplist:
        new_instance = new_plugin.get_plugin_instance()[0]
        if new_instance:
            new_instance._no_reorder = True
            new_instance.post_copy(old_plugin, plugins_ziplist)
    return new_plugins
