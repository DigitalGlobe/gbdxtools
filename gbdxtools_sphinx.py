from sphinx.ext.autodoc import FunctionDocumenter, MethodDocumenter

class MetaCatDocumenter(MethodDocumenter):
    objtype = 'catmeta'
    directivetype = 'method'

    def format_name(self):
        name = super(MethodDocumenter, self).format_name()
        name = name.replace('GeoDaskImage', 'CatalogImage')
        name = name.replace('DaskImage', 'CatalogImage')
        name = name.replace('PlotMixin', 'CatalogImage')
        name = name.replace('util', 'CatalogImage')
        return name

def setup(app):
    app.add_autodocumenter(MetaCatDocumenter)