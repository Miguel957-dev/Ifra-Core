import ifcopenshell
import ifcopenshell.geom
from calculos import calcular_vao
# ─────────────────────────────────────────
#  CONFIGURAÇÕES GLOBAIS
# ─────────────────────────────────────────
modelo = ifcopenshell.open('C:/Users/Miguel Lucas/Downloads/GitHub/InfraCore/Projeto_casa_Infracore.ifc')


# ─────────────────────────────────────────
#  FUNÇÃO AUXILIAR — altura real do pilar
# ─────────────────────────────────────────
def obter_altura_pilar(pilar, verts_z):
    """Tenta extrair a altura real via extrusão IFC.
    Se não encontrar, usa bounding box como fallback."""
    altura = None
    for rep in pilar.Representation.Representations:
        for item in rep.Items:
            if item.is_a("IfcExtrudedAreaSolid"):
                if altura is None or item.Depth > altura:
                    altura = item.Depth
            elif item.is_a("IfcMappedItem"):
                for sub in item.MappingSource.MappedRepresentation.Items:
                    if sub.is_a("IfcExtrudedAreaSolid"):
                        if altura is None or sub.Depth > altura:
                            altura = sub.Depth
    if altura is None:
        altura = max(verts_z) - min(verts_z)  # fallback: bounding box
    return altura


# ─────────────────────────────────────────
#  FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────
def extrair_geo(modelo):

    medidas_vigas         = []
    posiçao_viga          = []
    posiçao_pilar         = []
    medida_pilar          = []
    alturas_pilar         = []
    pi_reais              = []
    direçao_X             = {}
    direçao_Y             = {}
    viga_baldr_horizontal = []
    viga_baldr_vertical   = []
    viga_completa         = []
    vigas_aera_horizontal = []
    vigas_aereas_vertical = []
    todas_vigas_temp      = []
    corte_cz              = 0

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    li_pilar = modelo.by_type("IfcColumn")
    lis_viga  = modelo.by_type("IfcBeam")

    print(f"Vigas encontradas : {len(lis_viga)}")
    print(f"Pilares encontrados: {len(li_pilar)}")

    # ── PILARES ──────────────────────────
    for pilar in li_pilar:
        shape = ifcopenshell.geom.create_shape(settings, pilar)
        verts = shape.geometry.verts

        pilar_xs = verts[0::3]
        pilar_ys = verts[1::3]
        pilar_zs = verts[2::3]

        # Dimensões (bounding box)
        pilar_dx = max(pilar_xs) - min(pilar_xs)
        pilar_dy = max(pilar_ys) - min(pilar_ys)
        pilar_dz = max(pilar_zs) - min(pilar_zs)

        # Centro geométrico
        pilar_cx = (max(pilar_xs) + min(pilar_xs)) / 2
        pilar_cy = (max(pilar_ys) + min(pilar_ys)) / 2
        pilar_cz = (max(pilar_zs) + min(pilar_zs)) / 2

        

        # Altura real via extrusão IFC
        altura_real = obter_altura_pilar(pilar, pilar_zs)

        print(f"  Seção X:{pilar_dx:.3f} Y:{pilar_dy:.3f} | Altura:{altura_real:.3f} | Pos:({pilar_cx:.3f}, {pilar_cy:.3f}, {pilar_cz:.3f})")

        medida_pilar.append({'Tamanho eixo X': pilar_dx, 'Tamanho eixo Y': pilar_dy, 'Tamanho eixo Z': pilar_dz})
        posiçao_pilar.append({'Direção X': pilar_cx, 'Direção Y': pilar_cy, 'Direção Z': pilar_cz})
        alturas_pilar.append(pilar_dz)
    
   

    # Filtro baldrame — pilares com altura abaixo da média são ignorados
    if alturas_pilar:
        diferença    = max(alturas_pilar) - min(alturas_pilar)
        for i, pilar in enumerate(posiçao_pilar):
            if alturas_pilar[i] > diferença:
                pi_reais.append(pilar)

    # ── VIGAS ────────────────────────────
    print("\nVIGAS")
    for viga in lis_viga:
        shape = ifcopenshell.geom.create_shape(settings, viga)
        verts = shape.geometry.verts

        viga_xs = verts[0::3]
        viga_ys = verts[1::3]
        viga_zs = verts[2::3]
        
        
        viga_dx = max(viga_xs) - min(viga_xs)
        viga_dy = max(viga_ys) - min(viga_ys)
        viga_dz = max(viga_zs) - min(viga_zs)

        viga_cx = (max(viga_xs) + min(viga_xs)) / 2
        viga_cy = (max(viga_ys) + min(viga_ys)) / 2
        viga_cz = (max(viga_zs) + min(viga_zs)) / 2

        
        viga_completa = {
                'EIXO X': viga_dx,
                'EIXO Y': viga_dy,
                'ALTURA': viga_dz,
                'cx': viga_cx,
                'cy': viga_cy,
                'cz': viga_cz,
                'xmin': min(viga_xs),
                'xmax': max(viga_xs),
                'ymin': min(viga_ys),
                'ymax': max(viga_ys),
            }
        todas_vigas_temp.append(viga_completa)
        posiçao_viga.append({'Direção X': viga_cx, 'Direção Y': viga_cy, 'Direção Z': viga_cz})
        medidas_vigas.append({'Tamanho eixo X': viga_dx, 'Tamanho eixo Y': viga_dy, 'Tamanho eixo Z': viga_dz})

        print(f"  Dim X:{viga_dx:.3f} Y:{viga_dy:.3f} Z:{viga_dz:.3f} | Pos:({viga_cx:.3f}, {viga_cy:.3f}, {viga_cz:.3f})")

    todos_cz = [v['cz'] for v in todas_vigas_temp]
    corte_cz = (max(todos_cz) + min(todos_cz)) / 2

    for v in todas_vigas_temp:
        if v['cz'] < corte_cz:
            if v['EIXO X'] > v['EIXO Y']:
                viga_baldr_horizontal.append({'viga': v, 'pilares': [], 'vaos': [], 'apoio_viga': []})
            else:
                viga_baldr_vertical.append({'viga': v, 'pilares': [], 'vaos': [], 'apoio_viga': []})
        else:
            if v['EIXO X'] > v['EIXO Y']:
                vigas_aera_horizontal.append({'viga': v, 'pilares': [], 'vaos': [], 'apoio_viga': []})
            else:
                vigas_aereas_vertical.append({'viga': v, 'pilares': [], 'vaos': [], 'apoio_viga': []})

    # ── AGRUPAMENTO POR FILA X ───────────
    print("\nFILAS DE PILARES (eixo X)")
    for p in pi_reais:
        chave = p['Direção X']
        encontrou = False
    
        for cha in direçao_X:
            if abs(cha - chave) < 0.10:
                direçao_X[cha].append(p)
                encontrou = True
                break  
    
        if not encontrou:
            direçao_X[chave] = []
            direçao_X[chave].append(p)

    for chave, pilares in direçao_X.items():
        print(f"  Fila X ≈ {chave:.2f} → {len(pilares)} pilar(es)")
        for p in pilares:
            print(f"    X:{p['Direção X']:.2f} | Y:{p['Direção Y']:.2f}")

    # SEPARAÇÃO DE PILARES EIXO Y
    print("\nFILAS DE PILARES (eixo Y)")
    for p in pi_reais:
        chave = p['Direção Y']
        encontrou = False
    
        for cha in direçao_Y:
            if abs(cha - chave) < 0.10:
                direçao_Y[cha].append(p)
                encontrou = True
                break  
    
        if not encontrou:
            direçao_Y[chave] = []
            direçao_Y[chave].append(p)

    for chave, pilares in direçao_Y.items():
        print(f"  Fila Y ≈ {chave:.2f} → {len(pilares)} pilar(es)")
        for p in pilares:
            print(f"    Y:{p['Direção Y']:.2f} | X:{p['Direção X']:.2f}")

    # AGRUPAMENTO DE PILARES E VIGAS AEREAS HORIZONTAIS 
     
    for item in vigas_aera_horizontal:
        cx_vigama = item['viga']['xmax']
        cx_vigamin = item['viga']['xmin']
        cy_vigama = item['viga']['ymax'] 
        cy_vigamin = item['viga']['ymin'] 
        for ch in pi_reais:
            l = ch['Direção X']
            g = ch['Direção Y']
            
            if (cx_vigamin - 0.15 )<= l <= (cx_vigama + 0.15):
                if (cy_vigamin - 0.15 )<= g <= (cy_vigama + 0.15):
                    item['pilares'].append(ch)
        item['pilares'] = sorted(item['pilares'], key=lambda x1: x1['Direção X'])

    # AGRUPAMENTO DE PILARES E VIGAS AEREAS VERTICAIS 
    
    for ite in vigas_aereas_vertical:
        cx_vigama = ite['viga']['xmax']
        cx_vigamin = ite['viga']['xmin']
        cy_vigama = ite['viga']['ymax'] 
        cy_vigamin = ite['viga']['ymin'] 
        for c in pi_reais:
            m = c['Direção X']
            n = c['Direção Y']
            
            if (cx_vigamin - 0.15 )<= m <= (cx_vigama + 0.15):
                if (cy_vigamin - 0.15 )<= n <= (cy_vigama + 0.15):
                    ite['pilares'].append(c)
        ite['pilares'] = sorted(ite['pilares'], key=lambda y: y['Direção Y'])

    # AGRUPAMENTO DE PILARES E VIGAS  BALDRAMES AEREAS HORIZONTAIS 
     
    for item in viga_baldr_horizontal:
        cxb_vigama = item['viga']['xmax']
        cxb_vigamin = item['viga']['xmin']
        cyb_vigama = item['viga']['ymax'] 
        cyb_vigamin = item['viga']['ymin'] 
        for chb in pi_reais:
            lb = chb['Direção X']
            gb = chb['Direção Y']
            
            if (cxb_vigamin - 0.15 )<= lb <= (cxb_vigama + 0.15):
                if (cyb_vigamin - 0.15 )<= gb <= (cyb_vigama + 0.15):
                    item['pilares'].append(chb)
        item['pilares'] = sorted(item['pilares'], key=lambda x1: x1['Direção X'])

    # AGRUPAMENTO DE PILARES E VIGAS BALDRAMES AEREAS VERTICAIS 
    
    for ite in viga_baldr_vertical:
        cx_vigama = ite['viga']['xmax']
        cx_vigamin = ite['viga']['xmin']
        cy_vigama = ite['viga']['ymax'] 
        cy_vigamin = ite['viga']['ymin'] 
        for cb in pi_reais:
            mb = cb['Direção X']
            nb = cb['Direção Y']
            
            if (cx_vigamin - 0.15 )<= mb <= (cx_vigama + 0.15):
                if (cy_vigamin - 0.15 )<= nb <= (cy_vigama + 0.15):
                    ite['pilares'].append(cb)
        ite['pilares'] = sorted(ite['pilares'], key=lambda y: y['Direção Y'])

    # VERIFICAÇÃO SE TEM ALGUMA VIGA QUE ESTAR APOIADA EM OUTRA VIGA 

    for viga_h in vigas_aera_horizontal:
        xma = viga_h['viga']['xmax']
        xim = viga_h['viga']['xmin']
        if len(viga_h['pilares']) < 2:
            px = viga_h['pilares'][0]['Direção X']
            for viga_v in vigas_aereas_vertical:
                if (viga_v['viga']['xmin']) <= xim <= (viga_v['viga']['xmax']):
                    if viga_v['viga']['ymin'] <= viga_h['viga']['cy'] <= viga_v['viga']['ymax']:
                        vao = abs(px - xim)
                        viga_h['vaos'].append(vao)
                        viga_h['apoio_viga'].append([viga_v, 'apoiada no xmin'])
                if (viga_v['viga']['xmin']) <= xma <= (viga_v['viga']['xmax']):
                    if viga_v['viga']['ymin'] <= viga_h['viga']['cy'] <= viga_v['viga']['ymax']:
                        vao = abs(px - xma)
                        viga_h['vaos'].append(vao)
                        viga_h['apoio_viga'].append([viga_v, 'Apoiada no xmax'])

    # VERIFICAÇÃO INVERSA DE VIGAS VERTICAIS SE TEM ALGUMA VIGA QUE ESTAR APOIADA EM OUTRA VIGA 

    for viga_vv in vigas_aereas_vertical:
        yma = viga_vv['viga']['ymax']
        yim = viga_vv['viga']['ymin']
        if len(viga_vv['pilares']) < 2:
            px = viga_h['pilares'][0]['Direção X']
            for viga_hv in vigas_aera_horizontal:
                if (viga_hv['viga']['ymin']) <= yim <= (viga_hv['viga']['ymax']):
                    if viga_hv['viga']['xmin'] <= viga_vv['viga']['cx'] <= viga_hv['viga']['xmax']:
                        vao = abs(px - yim)
                        viga_vv['vaos'].append(vao)
                        viga_vv['apoio_viga'].append([viga_hv, 'apoiada no ymin'])
                if (viga_hv['viga']['ymin']) <= yma <= (viga_hv['viga']['ymax']):
                    if viga_hv['viga']['xmin'] <= viga_vv['viga']['cx'] <= viga_hv['viga']['xmax']:
                        vao = abs(px - yma)
                        viga_vv['vaos'].append(vao)
                        viga_vv['apoio_viga'].append([viga_hv, 'Apoiada no ymax'])

    # VERIFICAÇÃO SE TEM ALGUMA VIGA QUE ESTAR APOIADA EM OUTRA VIGA BALDRAMES

    for viga_bh in viga_baldr_horizontal:
        xma = viga_bh['viga']['xmax']
        xim = viga_bh['viga']['xmin']
        if len(viga_bh['pilares']) < 2:
            px = viga_bh['pilares'][0]['Direção X']
            for viga_bv in viga_baldr_vertical:
                if (viga_bv['viga']['xmin']) <= xim <= (viga_bv['viga']['xmax']):
                    if viga_bv['viga']['ymin'] <= viga_bh['viga']['cy'] <= viga_bv['viga']['ymax']:
                        vao = abs(px - xim)
                        viga_bh['vaos'].append(vao)
                        viga_bh['apoio_viga'].append([viga_bv, 'apoiada no xmin'])
                if (viga_bv['viga']['xmin']) <= xma <= (viga_bv['viga']['xmax']):
                    if viga_bv['viga']['ymin'] <= viga_bh['viga']['cy'] <= viga_bv['viga']['ymax']:
                        vao = abs(px - xma)
                        viga_bh['vaos'].append(vao)
                        viga_bh['apoio_viga'].append([viga_bv, 'Apoiada no xmax'])

    # BALDRAMES VERIFICAÇÃO INVERSA DE VIGAS VERTICAIS SE TEM ALGUMA VIGA QUE ESTAR APOIADA EM OUTRA VIGA 

    for viga_vbv in viga_baldr_vertical:
        yma = viga_vbv['viga']['ymax']
        yim = viga_vbv['viga']['ymin']
        if len(viga_vbv['pilares']) < 2:
            px = viga_bh['pilares'][0]['Direção X']
            for viga_hbv in viga_baldr_horizontal:
                if (viga_hbv['viga']['ymin']) <= yim <= (viga_hbv['viga']['ymax']):
                    if viga_hbv['viga']['xmin'] <= viga_vbv['viga']['cx'] <= viga_hbv['viga']['xmax']:
                        vao = abs(px - yim)
                        viga_vbv['vaos'].append(vao)
                        viga_vbv['apoio_viga'].append([viga_hbv, 'apoiada no ymin'])
                if (viga_hbv['viga']['ymin']) <= yma <= (viga_hbv['viga']['ymax']):
                    if viga_hbv['viga']['xmin'] <= viga_vbv['viga']['cx'] <= viga_hbv['viga']['xmax']:
                        vao = abs(px - yma)
                        viga_vbv['vaos'].append(vao)
                        viga_vbv['apoio_viga'].append([viga_hbv, 'Apoiada no ymax'])

    # CALCULAR VÃO DAS VIGAS HORIZONTAIS 

    for vh in vigas_aera_horizontal:
        for i in range(len(vh['pilares']) - 1):
            primeiro = vh['pilares'][i] 
            segundo = vh['pilares'][i + 1]
            x1 = primeiro['Direção X']
            y1 = primeiro['Direção Y']
            x2 = segundo['Direção X']
            y2 = segundo['Direção Y']

            vao = calcular_vao(x1, y1, x2, y2)
            
            vh['vaos'].append(vao)

    # CALCULAR VÃO DAS VIGAS VERTICAIS
    for vv in vigas_aereas_vertical:
        for i in range(len(vv['pilares']) - 1):
            primeiro = vv['pilares'][i] 
            segundo = vv['pilares'][i + 1]
            x1 = primeiro['Direção X']
            y1 = primeiro['Direção Y']
            x2 = segundo['Direção X']
            y2 = segundo['Direção Y']
            
            vao = calcular_vao(x1, y1, x2, y2)
            
            vv['vaos'].append(vao)

    # CALCULAR VÃO DAS VIGAS BALDRAMES HORIZONTAIS 

    for vbh in viga_baldr_horizontal:
        for i in range(len(vbh['pilares']) - 1):
            primeiro = vbh['pilares'][i] 
            segundo = vbh['pilares'][i + 1]
            x1 = primeiro['Direção X']
            y1 = primeiro['Direção Y']
            x2 = segundo['Direção X']
            y2 = segundo['Direção Y']

            vao = calcular_vao(x1, y1, x2, y2)
            
            vbh['vaos'].append(vao)

    # CALCULAR VÃO DAS VIGAS BALDRAMES VERTICAIS 

    for vbv in viga_baldr_vertical:
        for i in range(len(vbv['pilares']) - 1):
            primeiro = vbv['pilares'][i] 
            segundo = vbv['pilares'][i + 1]
            x1 = primeiro['Direção X']
            y1 = primeiro['Direção Y']
            x2 = segundo['Direção X']
            y2 = segundo['Direção Y']
            
            vao = calcular_vao(x1, y1, x2, y2)
            
            vbv['vaos'].append(vao)
            

    print(f"\nPilares reais (sem baldrame): {len(pi_reais)}")

    print('-----VIGAS HORIZONTAIS BALDRAMES-----')
    print()
    for z in viga_baldr_horizontal:
        print(z)
        print()
    print('-----VIGAS VERTICAL BALDRAMES-----')
    print()
    for x in viga_baldr_vertical:
        print(x)
        print()
    print('----VIGAS HORIZONTAIS AEREAS-----')
    print()
    for o in vigas_aera_horizontal:
        print(o)
        print()
    print('-----VIGAS VERTICAIS AEREAS-----')
    print()
    for b in vigas_aereas_vertical:
        print(b)
        print()
   
    return medidas_vigas, posiçao_viga, vigas_aera_horizontal, vigas_aereas_vertical, viga_baldr_horizontal, viga_baldr_vertical, pi_reais


# ─────────────────────────────────────────
#  EXECUÇÃO
# ─────────────────────────────────────────
extrair_geo(modelo)