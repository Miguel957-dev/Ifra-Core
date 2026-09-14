
def calcular_vao(x1, y1, x2, y2):
    if y1 == y2:
        maior_valor_X = max(x1, x2)
        menor_valor_X = min(x1, x2)
        vao = maior_valor_X - menor_valor_X
        print(f"O valor do vão da viga é de {vao} METROS")
    elif x1 == x2:
        maior_valor_Y = max(y1, y2)
        menor_valor_Y = min(y1, y2)
        vao = maior_valor_Y - menor_valor_Y
        print(f"O valor do vão da viga é de {vao} METROS")
    else:
        maior_valor_Y = max(y1, y2)
        menor_valor_Y = min(y1, y2)
        cateto_Y = maior_valor_Y - menor_valor_Y
        maior_valor_X = max(x1, x2)
        menor_valor_X = min(x1, x2)
        cateto_X = maior_valor_X - menor_valor_X
        hip =(cateto_X ** 2) + (cateto_Y ** 2)
        vao = hip ** 0.5
        print(f"O valor do vão da viga é de {vao:.5f} METROS")
    return vao

def dimensionar_vigas():
    pass 
