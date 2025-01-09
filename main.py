import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(usuario, senha, driver):
    username = driver.find_element(By.ID, 'txtUsuario')
    username.send_keys('carlos.daniel@sead.pi.gov.br')

    password = driver.find_element(By.ID, 'pwdSenha')
    password.send_keys('7APjOcSosf')

    select_element = driver.find_element(By.ID, "selOrgao")
    dropdown = Select(select_element)
    dropdown.select_by_visible_text("SEAD-PI")

    password.send_keys(Keys.RETURN)


def info_processo(driver, wait):
    # print("Entrei no processo")
    
    str_documentos = []

    # wait.until(EC.presence_of_element_located((By.ID, "ifrArvore")))

    # iframe_arvore = driver.find_element(By.ID, "ifrArvore")
    # driver.switch_to.frame(iframe_arvore)

    # div_container = driver.find_element(By.ID, 'container')
    # div_arvore = div_container.find_element(By.ID, 'divArvore')
    # div = div_arvore.find_element(By.CLASS_NAME, 'infraArvore')

    # tags_com_target = div.find_elements(By.CSS_SELECTOR, "[target='ifrVisualizacao']")
    # print(len(tags_com_target))
    
    i=0
    while True:

        wait.until(EC.presence_of_element_located((By.ID, "ifrArvore")))

        iframe_arvore = driver.find_element(By.ID, "ifrArvore")
        driver.switch_to.frame(iframe_arvore)

        div_container = driver.find_element(By.ID, 'container')
        div_arvore = div_container.find_element(By.ID, 'divArvore')
        div = div_arvore.find_element(By.CLASS_NAME, 'infraArvore')

        tags_com_target = div.find_elements(By.CSS_SELECTOR, "[target='ifrVisualizacao']")

        # print('Quantidade de documentos no processo: ', len(tags_com_target))

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[target='ifrVisualizacao']")))
        tags_com_target = div.find_elements(By.CSS_SELECTOR, "[target='ifrVisualizacao']")

        # Rolagem para o elemento
        driver.execute_script("arguments[0].scrollIntoView(true);", tags_com_target[i])

        span_elements = tags_com_target[i].find_elements(By.TAG_NAME, "span")
        
        if span_elements:
            # Simular clique com JavaScript (caso o clique direto falhe)
            driver.execute_script("arguments[0].click();", tags_com_target[i])
        else:
            pass

        str_documentos.append(entendimento_documento(driver, wait, i))
        
        i+=1

        if i == len(tags_com_target):
            driver.switch_to.default_content()
            break

        driver.switch_to.default_content()
    
    driver.refresh()
    driver.switch_to.default_content()

    dialogo_processo(str_documentos)    


def entendimento_documento(driver, wait, i):
    # print("Entrei no documento ", (i+1))

    driver.switch_to.default_content()
    iframe_visualizacao = driver.find_element(By.ID, "ifrVisualizacao")

    driver.switch_to.frame(iframe_visualizacao)

    wait.until(EC.presence_of_element_located((By.ID, "ifrArvoreHtml")))

    iframe = driver.find_element(By.ID, "ifrArvoreHtml")
    driver.switch_to.frame(iframe)
    body = driver.find_element(By.TAG_NAME, "body")

    paragraphs = body.find_elements(By.TAG_NAME, "p")
    concatenated_text = " ".join([p.text for p in paragraphs])

    return concatenated_text


def dialogo_processo(str_documentos):
    for i in range(len(str_documentos)):
        print('Documento ', (i+1))
        print(str_documentos[i])


def varredura_pagina():

    selected_page = input("Digite a página em que deseja realizar a varredura: ")

    url_inicial = chrome_driver.current_url

    wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))
    page = chrome_driver.find_element(By.ID, "selRecebidosPaginacaoSuperior")
    dropdown = Select(page)
    dropdown.select_by_visible_text(selected_page)

    processos = chrome_driver.find_elements(By.CLASS_NAME, "processoVisualizado")
    print(f"Quantidade de processos encontrados: {len(processos)}")

    for i in range(len(processos)):

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "processoVisualizado")))
        processos = chrome_driver.find_elements(By.CLASS_NAME, "processoVisualizado")
        print(f"{i+1}º Processo: {processos[i].text}")
        wait.until(EC.presence_of_element_located((By.ID, "divInfraAreaGlobal")))

        processos[i].click()
        info_processo(driver=chrome_driver, wait=wait)

        chrome_driver.get(url_inicial)
        wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))


def dialogar_processo_especifico():
    
    url_inicial = chrome_driver.current_url
 
    wait.until(EC.presence_of_element_located((By.ID, "divInfraBarraSistemaD")))
    div_infra_barra = chrome_driver.find_element(By.ID, "divInfraBarraSistemaD")
    form_search = div_infra_barra.find_element(By.ID, "frmProtocoloPesquisaRapida")
    input_search = form_search.find_element(By.ID, "txtPesquisaRapida")

    process_number = input("Digite o número do processo que deseja inspecionar: ")

    input_search.send_keys(process_number)
    input_search.send_keys(Keys.RETURN)


menu = "============\n= 1 = Realizar varredura de página com 1 único prompt\n= 2 = Dialogar com um processo em específico\n============\n= "

if __name__ == "__main__":

    chrome_driver = webdriver.Chrome()
    chrome_driver.get('https://sip.pi.gov.br/sip/login.php?sigla_orgao_sistema=GOV-PI&sigla_sistema=SEI&infra_url=L3NlaS8=')
    wait = WebDriverWait(chrome_driver, 10)
    
    usuario = "carlos.daniel@sead.pi.gov.br"
    senha = "7APjOcSosf"

    menu_opt = input(menu)

    login(usuario, senha, driver=chrome_driver)

    if menu_opt == "1":
        varredura_pagina()
    elif menu_opt == "2":
        dialogar_processo_especifico()

    # url_inicial = chrome_driver.current_url

    # wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))
    # page = chrome_driver.find_element(By.ID, "selRecebidosPaginacaoSuperior")
    # dropdown = Select(page)
    # dropdown.select_by_visible_text("13")

    # processos = chrome_driver.find_elements(By.CLASS_NAME, "processoVisualizado")
    # print(f"Quantidade de processos encontrados: {len(processos)}")

    # for i in range(len(processos)):

    #     wait.until(EC.presence_of_element_located((By.CLASS_NAME, "processoVisualizado")))
    #     processos = chrome_driver.find_elements(By.CLASS_NAME, "processoVisualizado")
    #     print(f"{i+1}º Processo: {processos[i].text}")
    #     wait.until(EC.presence_of_element_located((By.ID, "divInfraAreaGlobal")))

    #     processos[i].click()
    #     info_processo(driver=chrome_driver, wait=wait)

    #     chrome_driver.get(url_inicial)
    #     wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))