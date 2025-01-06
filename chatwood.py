import requests
import os

CHATWOOT_APIKEY = 'dummy_api_key'
CHATWOOT_ACCOUNT_ID = 'dummy_account_id'

def find_contact_by_phone(phone_number):
    url = f"https://app.chatwoot.com/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts/search?q={phone_number}"
    headers = {
        'api_access_token': CHATWOOT_APIKEY,
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        contacts = response.json()
        if len(contacts['payload']) > 0:
            return contacts['payload'][0] # Retorna el primer contacto encontrado
    return None

def create_contact(phone_number, name, email, inbox_id):
    url = f"https://app.chatwoot.com/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts"
    headers = {
        'api_access_token': CHATWOOT_APIKEY,
        'Content-Type': 'application/json'
    }
    
    contact_data = {
        "phone_number": phone_number,
        "name": name,
        "email": email,
        "inbox_id": inbox_id,
    }
    
    response = requests.post(url, json=contact_data, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Retorna el contacto creado
    else:
        print("Error al crear el contacto:", response.status_code, response.text)
        return None

def send_chatwoot_message(contact_id,inbox_id, source_id,name):
    url = f"https://app.chatwoot.com/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations"
    headers = {
        'api_access_token': CHATWOOT_APIKEY,
        'Content-Type': 'application/json'
    }
    
    conversation_data = {
        "source_id": source_id, 
        "inbox_id": inbox_id, 
        "contact_id": contact_id,
        "message": {  
            "content": f"Hola {name}! ¿Cómo estás?\n\nVimos que te inscribiste a los cursos del Trastorno Limite de la Personalidad, ambos con certificación auspiciada por el Colegio de Psicólogos de Santiago del Estero + Analítico de conocimientos adquiridos.\n\nCada curso acredita 15 hs. Cátedra Teórico-Prácticas.\n\n💻Modalidad: Virtual, intensivo en vivo (grabación disponible por un año).\n\n¿Te gustaría aprovechar la promoción disponible y terminar tu inscripción? Avísanos así te compartimos el link de pago.",
        }
    }

    response = requests.post(url, json=conversation_data, headers=headers)

    if response.status_code == 200:
        print("Mensaje enviado con éxito")
    else:
        print("Error al enviar el mensaje:", response.status_code, response.text)

def main(phone_number, source_id, name, email, inbox_id):
    contact = find_contact_by_phone(phone_number)
    

    if contact:
        print("Contacto encontrado")
        send_chatwoot_message(contact['id'], inbox_id, source_id, name)
    else:
        print("Contacto no encontrado, creando uno nuevo...")
        new_contact = create_contact(phone_number, name, email, inbox_id)['payload']['contact']
        if new_contact:
            print(new_contact)
            send_chatwoot_message(new_contact['id'],inbox_id, source_id, name)



phone_number = "+1234567890"
source_id = "1234567890"
name = "Nombre de Ejemplo"
email = "ejemplo@correo.com"
inbox_id = 12345


main(phone_number, source_id, name, email, inbox_id)
