import numpy as np
from gnuradio import gr

class wavelet_edge_detector(gr.sync_block):
    def __init__(self, vector_length=1024, scale=10):
        gr.sync_block.__init__(self, name="Wavelet Edge Detector",
            in_sig=[(np.float32, vector_length)],
            out_sig=[(np.float32, vector_length)])
        self.vector_length = vector_length
        self.scale = scale

    def work(self, input_items, output_items):
        # input_items[0][0] es tu espectro S(n)
        s_n = input_items[0][0]
        
        # Creamos la Wavelet B-spline cúbica (simplificada para detección de bordes)
        # Una escala grande (j=10) significa un filtro de suavizado muy ancho
        # que resalta las transiciones lentas (banda ancha)
        
        # Simulamos la derivada de una Gaussiana (comportamiento similar a spline en bordes)
        points = np.arange(-self.vector_length//2, self.vector_length//2)
        wavelet = -points * np.exp(-(points**2) / (2 * (self.scale**2)))
        
        # Convolución para obtener los coeficientes wavelet d_j(n)
        # Esto es lo que ves en la Figura 6(b) del paper
        coeffs = np.convolve(s_n, wavelet, mode='same')
        
        output_items[0][0][:] = coeffs
        return len(output_items[0])
