import pygame

# Resolución de referencia usada en los mockups (1920×1080)
REF_WIDTH_CM  = 33.867  # 1920 px en cm
REF_HEIGHT_CM = 19.05   # 1080 px en cm

def get_responsive_rect(x_cm, y_cm, w_cm, h_cm, screen):
    """
    Convierte posiciones y tamaños en centímetros (según el mockup base 1920×1080)
    a un pygame.Rect escalado al tamaño actual de la pantalla.

    :param x_cm: Posición horizontal en cm (desde izquierda)
    :param y_cm: Posición vertical en cm (desde arriba)
    :param w_cm: Ancho en cm
    :param h_cm: Alto en cm
    :param screen: pygame.Surface activa (pantalla)
    :return: pygame.Rect ajustado proporcionalmente
    """
    if not hasattr(screen, "get_size"):
        raise TypeError("El argumento 'screen' debe ser una superficie válida de Pygame.")

    screen_width, screen_height = screen.get_size()

    x_px = int((x_cm / REF_WIDTH_CM)  * screen_width)
    y_px = int((y_cm / REF_HEIGHT_CM) * screen_height)
    w_px = int((w_cm / REF_WIDTH_CM)  * screen_width)
    h_px = int((h_cm / REF_HEIGHT_CM) * screen_height)

    return pygame.Rect(x_px, y_px, w_px, h_px)