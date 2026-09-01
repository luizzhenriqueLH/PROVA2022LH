"""
Propósito: Dividir as questões por padrão visual vertical.
Autor: Alexandre Nassar de Peder (modificado)
Criação: 02/10/2025
Atualização: 03/06/2026
"""

from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_padrao(imagem, cor_alvo, tolerancia=15, altura_esperada=4, margem_altura=2):
    """
    Encontra posições no último pixel da direita com a cor especificada
    e altura entre (altura_esperada - margem) e (altura_esperada + margem).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    coluna_x = largura - 1  # Último pixel da direita
    
    altura_min = max(1, altura_esperada - margem_altura)  # ex: 2px
    altura_max = altura_esperada + margem_altura          # ex: 6px
    
    y = 0
    while y < altura:
        # Verifica se o pixel atual combina com a cor alvo
        pixel = pixels[coluna_x, y]
        r, g, b = pixel[:3]
        
        if (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia):
            
            # Conta a altura real do bloco de cor contínuo
            inicio_y = y
            altura_contador = 0
            
            while y < altura:
                p_atual = pixels[coluna_x, y][:3]
                if (abs(p_atual[0] - cor_alvo[0]) <= tolerancia and 
                    abs(p_atual[1] - cor_alvo[1]) <= tolerancia and 
                    abs(p_atual[2] - cor_alvo[2]) <= tolerancia):
                    altura_contador += 1
                    y += 1
                else:
                    break
            
            # Valida se a altura encontrada está dentro da margem de erro (2 a 6 px)
            if altura_min <= altura_contador <= altura_max:
                posicao_corte = inicio_y - 44  # Corta 44px antes do padrão
                if posicao_corte < 0:
                    posicao_corte = 0
                    
                posicoes_corte.append(posicao_corte)
                print(f"Padrão ({altura_contador}px) em y={inicio_y}, cortando em y={posicao_corte}")
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando nas posições identificadas
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_padrao(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} marcas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a parte final restante
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Atualize com o nome do seu arquivo
    pasta_saida = "questoes_divididas"                        # Atualize com o nome da pasta desejada

    # Cor RGB direta (35, 31, 32)
    cor_do_padrao = (35, 31, 32)
    print(f"Cor alvo configurada: RGB{cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")