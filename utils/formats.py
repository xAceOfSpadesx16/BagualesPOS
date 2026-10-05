def formatted_integer(integer):
    # Format with thousands separator (comma) then swap to dot for ES-AR style
    # 1000 -> "1,000" -> "1.000"
    return "{:,}".format(int(integer)).replace(",", ".")