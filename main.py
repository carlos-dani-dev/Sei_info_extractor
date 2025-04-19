import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.automatic_downloads": 2,
    "download.default_directory": "/dev/null",  # Diretório inválido para impedir downloads
    "download.prompt_for_download": False,  # Bloqueia pop-ups de download
    "download.directory_upgrade": False,
    "download.extensions_to_open": "applications/docx",  # Apenas PDF pode abrir, docx fica bloqueado
    "plugins.always_open_pdf_externally": False,  # Impede que PDFs sejam baixados automaticamente
    "safebrowsing.enabled": False,  # Evita avisos de segurança sobre downloads
})
chrome_options.add_argument(argument="--log-level=2")  # Suprime mensagens de INFO
# chrome_service = Service(executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")



def login(usuario, senha, driver):
    username = driver.find_element(By.ID, 'txtUsuario')
    username.send_keys('carlos.daniel@sead.pi.gov.br')

    password = driver.find_element(By.ID, 'pwdSenha')
    password.send_keys('7APjOcSosf')

    select_element = driver.find_element(By.ID, "selOrgao")
    dropdown = Select(select_element)
    dropdown.select_by_visible_text("SEAD-PI")

    password.send_keys(Keys.RETURN)


def preprocess_doc(texto):

    # Remover quebras de linha desnecessárias
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    # Extrair as informações essenciais
    padrao = re.compile(
    r"(PROCESSO Nº:.*?Documento assinado eletronicamente)",
    re.DOTALL
    )
    
    match = padrao.search(texto)
    
    if match:
        texto_limpo = match.group(0)
        # print('texto: '+texto+'\n'+'texto limpo: '+texto_limpo)
        return texto_limpo

    return ""


def chatgpt_api_interaction(predef_prompt, str_documentos):
    
    # textos = []

    # for doc in docs:
    #     textos.append(preprocess_doc(doc))

    string_textos = ""

    for texto in str_documentos:
        string_textos += texto + "\n"

    prompt = f"\n{string_textos}\n{predef_prompt}\n"
    tamanho_prompt = len(prompt)
    if tamanho_prompt > 3000:
        prompt = prompt[tamanho_prompt-3000:-1]
    else:
        prompt = prompt[:-1]
    print('= prompt para o ChatGPT: ',prompt)

    return "= ========= Resposta do ChatGPT ========="


def info_processo(driver, wait, predef_prompt):

    str_documentos = []    
    i=0    

    wait.until(EC.presence_of_element_located((By.ID, "ifrArvore")))

    iframe_arvore = driver.find_element(By.ID, "ifrArvore")
    driver.switch_to.frame(iframe_arvore)

    div_container = driver.find_element(By.ID, 'container')
    div_arvore = div_container.find_element(By.ID, 'divArvore')
    div = div_arvore.find_element(By.CLASS_NAME, 'infraArvore')
    
    verifica_presenca_pasta(driver, div, wait)

    driver.switch_to.default_content()

    while True:
        wait.until(EC.presence_of_element_located((By.ID, "ifrArvore")))

        iframe_arvore = driver.find_element(By.ID, "ifrArvore")
        driver.switch_to.frame(iframe_arvore)

        div_container = driver.find_element(By.ID, 'container')
        div_arvore = div_container.find_element(By.ID, 'divArvore')
        div = div_arvore.find_element(By.CLASS_NAME, 'infraArvore')
    
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[target='ifrVisualizacao']")))
        tags_com_target = div.find_elements(By.CSS_SELECTOR, "[target='ifrVisualizacao']")

        driver.execute_script("arguments[0].scrollIntoView(true);", tags_com_target[i])

        span_elements = tags_com_target[i].find_elements(By.TAG_NAME, "span")
        
        if span_elements:
            driver.execute_script("arguments[0].click();", tags_com_target[i])
        else:
            pass

        str_documentos.append(preprocess_doc(entendimento_documento(driver, wait, i, predef_prompt)))
        
        i+=1
        if i == len(tags_com_target):
            driver.switch_to.default_content()
            break

        driver.switch_to.default_content()
    
    driver.refresh()
    driver.switch_to.default_content()

    answer = chatgpt_api_interaction(predef_prompt, str_documentos)
    
    return answer

def verifica_presenca_pasta(driver, div, wait):
    i=1
    while True:
        id = 'ancjoinPASTA'+str(i)
        
        try:
            ancjoin = div.find_element(By.ID, id)
        except:
            break
        else:
            img = ancjoin.find_element(By.TAG_NAME, "img")
            if "plus.gif" in img.get_attribute("src"):
                driver.execute_script("arguments[0].click();", ancjoin)
                time.sleep(2)
        i+=1 


def entendimento_documento(driver, wait, i, predef_prompt):
    
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


def varredura_pagina(predef_prompt):

    selected_page = input("= Página: ")

    url_inicial = chrome_driver.current_url

    wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))
    page = chrome_driver.find_element(By.ID, "selRecebidosPaginacaoSuperior")
    dropdown = Select(page)
    dropdown.select_by_visible_text(selected_page)

    processos = chrome_driver.find_elements(By.CLASS_NAME, "processoVisualizado")
    print(f"= Quantidade de processos encontrados na página {selected_page}: {len(processos)}")

    for i in range(len(processos)):

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "processoVisualizado")))
        processos = chrome_driver.find_elements(By.CLASS_NAME, "processoVisualizado")
        processo = processos[i].text
        print(f"= {i+1}º Processo: {processo}")
        wait.until(EC.presence_of_element_located((By.ID, "divInfraAreaGlobal")))

        processos[i].click()
        answer = info_processo(driver=chrome_driver, wait=wait, predef_prompt=predef_prompt)

        print(f"{processo}: {answer}")

        chrome_driver.get(url_inicial)
        wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))


def dialogar_processo_especifico():

    wait.until(EC.presence_of_element_located((By.ID, "divInfraBarraSistemaD")))
    div_infra_barra = chrome_driver.find_element(By.ID, "divInfraBarraSistemaD")
    form_search = div_infra_barra.find_element(By.ID, "frmProtocoloPesquisaRapida")
    input_search = form_search.find_element(By.ID, "txtPesquisaRapida")

    process_number = input("= Digite o número do processo que deseja inspecionar: ")

    input_search.send_keys(process_number)
    input_search.send_keys(Keys.RETURN)

    prompt = input(f"= Pergunte ao processo {process_number}: ")

    answer = info_processo(driver=chrome_driver, wait=wait, predef_prompt=prompt)

    print(f"{process_number}: {answer}")

def varrer_lista_processos(process_list):

    wait.until(EC.presence_of_element_located((By.ID, "divInfraBarraSistemaD")))
    div_infra_barra = chrome_driver.find_element(By.ID, "divInfraBarraSistemaD")
    form_search = div_infra_barra.find_element(By.ID, "frmProtocoloPesquisaRapida")
    input_search = form_search.find_element(By.ID, "txtPesquisaRapida")

    prompt = input("= Pergunte aos processos: ")

    for process_number in process_list:
        input_search.send_keys(process_number)
        input_search.send_keys(Keys.RETURN)

        answer = info_processo(driver=chrome_driver, wait=wait, predef_prompt=prompt)

        print(f"{process_number}: {answer}")


menu = "============\n= 1 = Realizar varredura de página com 1 único prompt\n= 2 = Dialogar com um processo em específico\n= 3 = Varrer lista de processos\n============\n= "

if __name__ == "__main__":

    process_list = []

    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.get('https://sip.pi.gov.br/sip/login.php?sigla_orgao_sistema=GOV-PI&sigla_sistema=SEI&infra_url=L3NlaS8=')
    wait = WebDriverWait(chrome_driver, 10)
    
    usuario = "carlos.daniel@sead.pi.gov.br"
    senha = "7APjOcSosf"

    menu_opt = input(menu)

    login(usuario, senha, driver=chrome_driver)

    if menu_opt == "1":
        predef_prompt = input("= Pergunta comum aos processos: ")
        varredura_pagina(predef_prompt)
    elif menu_opt == "2":
        dialogar_processo_especifico()
    elif menu_opt == "3":
        print("A lista de processos já foi predefinida")
        varrer_lista_processos(process_list)