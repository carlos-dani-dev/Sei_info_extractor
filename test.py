import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def inside_process_iteration(driver, wait):
    
    wait.until(EC.presence_of_element_located((By.ID, "container")))
    outer_div = driver.find_element(By.ID, "container")

    inner_div = driver.find_element(By.CLASS_NAME, "infraArvore")

    # Dentro da inner_div, localizar todas as tags <a> com os atributos id e target
    links = inner_div.find_elements(By.XPATH, ".//a[@id and @target]")
    print(len(links))

    return


# Inicializa o driver do Selenium
driver = webdriver.Chrome()

# Acessa a URL do sistema
driver.get('https://sip.pi.gov.br/sip/login.php?sigla_orgao_sistema=GOV-PI&sigla_sistema=SEI&infra_url=L3NlaS8=')
wait = WebDriverWait(driver, 10)
time.sleep(3)

# Login no sistema
username = driver.find_element(By.ID, 'txtUsuario')
username.send_keys('carlos.daniel@sead.pi.gov.br')

password = driver.find_element(By.ID, 'pwdSenha')
password.send_keys('7APjOcSosf')

select_element = driver.find_element(By.ID, "selOrgao")
dropdown = Select(select_element)
dropdown.select_by_visible_text("SEAD-PI")

password.send_keys(Keys.RETURN)

# Aguarda a tabela de processos carregar
wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))

# Seleciona a página na tabela de processos
page = driver.find_element(By.ID, "selRecebidosPaginacaoSuperior")
dropdown = Select(page)
dropdown.select_by_visible_text("13")

links = driver.find_elements(By.CLASS_NAME, "processoVisualizado")
qtt_links = len(links)
print(f"Quantidade de links encontrados: {qtt_links}")
    
for i in range(qtt_links):
    # Recarrega os links para evitar referências obsoletas
    links = driver.find_elements(By.CLASS_NAME, "processoVisualizado")

   # Imprime o número do processo
    print(f"{i+1}º Processo: {links[i].text}")

    # Clica no link do processo
    links[i].click()

    # Aguarda a página de detalhes carregar
    wait.until(EC.presence_of_element_located((By.ID, "divInfraAreaGlobal")))

    # iterando dentro do processo
    inside_process_iteration(driver, wait)

    # Volta para a página anterior
    driver.back()

    if "Confirmar reenvio do formulário" in driver.page_source or "ERR_CACHE_MISS" in driver.page_source:
            driver.back()
            time.sleep(3)

    # Aguarda a tabela recarregar
    wait.until(EC.presence_of_element_located((By.ID, "tblProcessosRecebidos")))

# Fecha o navegador
driver.quit()
