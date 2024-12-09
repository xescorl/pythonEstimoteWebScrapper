from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración de credenciales
email = "tuEmail"  # Reemplaza con tu correo
password = "tuContraseña"  # Reemplaza con tu contraseña

# Configurar el controlador de Selenium (Chrome en este caso)
driver = webdriver.Chrome()  # Asegúrate de que ChromeDriver está instalado y en tu PATH

# URL de Estimote Cloud
url = "https://cloud.estimote.com/"

try:
    # Abrir el navegador e ir a la página
    driver.get(url)
    time.sleep(1)  # Esperar a que cargue la página

    # Iniciar sesión
    driver.find_element(By.NAME, "username").send_keys(email)  # Campo de email
    driver.find_element(By.NAME, "password").send_keys(password)  # Campo de contraseña
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)  # Presionar Enter
    time.sleep(5)  # Esperar a que inicie sesión y cargue la página principal

    # Navegar a la sección de Beacons
    beacons_link = driver.find_element(By.LINK_TEXT, "Beacons")  # Ajusta si el texto es diferente
    beacons_link.click()
    time.sleep(3)  # Esperar a que cargue la página de Beacons

    # Esperar a que los elementos de la fila de beacons estén presentes
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.u-posRelative")))

    # Extraer datos de la tabla o elementos de los beacons
    beacons = []
    rows = driver.find_elements(By.CSS_SELECTOR, "li.u-posRelative")  # Ajusta el selector para filas

    # Verificar si se encontraron filas
    if not rows:
        print("No se encontraron filas de beacons. Verifica el selector CSS.")
        print(driver.page_source)  # Imprimir el HTML de la página para depuración
    else:
        for i in range(len(rows)):
            # Re-fetch the rows to avoid StaleElementReferenceException
            rows = driver.find_elements(By.CSS_SELECTOR, "li.u-posRelative")
            row = rows[i]

            # Hacer clic en la barra de configuración del beacon
            settings_button = row.find_element(By.CSS_SELECTOR, "a.Btn.Btn--md.Btn--outline.PendingSettings")  # Ajusta el selector
            
            # Scroll into view and wait until clickable
            driver.execute_script("arguments[0].scrollIntoView(true);", settings_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.Btn.Btn--md.Btn--outline.PendingSettings")))
            
            # Click the button using JavaScript
            driver.execute_script("arguments[0].click();", settings_button)
            
            time.sleep(1)  # Esperar a que se abra la configuración

            # Extraer Major y Minor
            major = driver.find_element(By.XPATH, "//div[contains(text(), 'Major')]/following-sibling::div").text
            minor = driver.find_element(By.XPATH, "//div[contains(text(), 'Minor')]/following-sibling::div").text

            beacons.append({
                "Major": major,
                "Minor": minor
            })

            # Volver a la lista completa de beacons
            driver.back()
            time.sleep(2)  # Esperar a que la página de la lista de beacons se cargue de nuevo

    # Guardar los datos en un archivo CSV
    df = pd.DataFrame(beacons)
    df.to_csv("estimote_beacons.csv", index=False)
    print("Datos exportados a estimote_beacons.csv")

finally:
    driver.quit()