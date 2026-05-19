def get_rapaport_shape(shape, fancy_color):
    if fancy_color and fancy_color.strip():
        return None
    return "BR" if shape.lower() == "round" else "PS"