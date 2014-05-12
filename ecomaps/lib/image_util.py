"""
Image utilities

@author rwilkinson
"""
from cStringIO import StringIO
try:
    from PIL import Image
except:
    import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo as FigureCanvas

def figureToImage(fig):
    
    canvas = FigureCanvas(fig)
    
    buffer = StringIO()
    canvas.print_figure(buffer, dpi=fig.get_dpi(), facecolor=fig.get_facecolor(), edgecolor=fig.get_edgecolor())
    buffer.reset()
    im = Image.open(buffer)
    
    return im
