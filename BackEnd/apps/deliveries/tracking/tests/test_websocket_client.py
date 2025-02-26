#!/usr/bin/env python
"""
Script para testar a conexão WebSocket de rastreamento de entregas.
Este script simula um cliente que envia atualizações de localização e status para o servidor.
"""

import asyncio
import json
import websockets
import random
import time
import sys
import argparse
import requests
from datetime import datetime

# Configurações padrão
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "8000"
DEFAULT_DELIVERY_ID = ""  # Precisa ser preenchido com um ID de entrega válido
DEFAULT_TOKEN = ""  # Precisa ser preenchido com um token JWT válido

# Coordenadas para simular um percurso (São Paulo para Rio de Janeiro)
ROUTE_COORDINATES = [
    # São Paulo
    {"lat": -23.550520, "lng": -46.633308},
    {"lat": -23.545634, "lng": -46.601465},
    {"lat": -23.510868, "lng": -46.456413},
    # Rodovia Presidente Dutra
    {"lat": -23.367068, "lng": -46.208878},
    {"lat": -23.187277, "lng": -45.887299},
    {"lat": -22.911615, "lng": -45.465698},
    {"lat": -22.798091, "lng": -45.192413},
    {"lat": -22.528393, "lng": -44.888153},
    {"lat": -22.408922, "lng": -44.764557},
    {"lat": -22.255080, "lng": -44.335861},
    {"lat": -22.169438, "lng": -44.147339},
    {"lat": -22.075548, "lng": -43.899078},
    # Rio de Janeiro
    {"lat": -22.911615, "lng": -43.714027},
    {"lat": -22.911615, "lng": -43.447571},
    {"lat": -22.911615, "lng": -43.217163},
    {"lat": -22.911615, "lng": -43.174591},
]

# Status de entrega para simular o progresso
DELIVERY_STATUSES = [
    "pending",
    "in_transit",
    "approaching",
    "arrived",
    "delivered"
]

async def get_token(host, port, username, password):
    """Obtém um token JWT do servidor."""
    url = f"http://{host}:{port}/api/token/"
    response = requests.post(url, json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json()["access"]
    else:
        print(f"Erro ao obter token: {response.status_code} - {response.text}")
        return None

async def send_location_updates(websocket, delivery_id, interval=5):
    """Envia atualizações de localização para o servidor."""
    for i, coord in enumerate(ROUTE_COORDINATES):
        # Calcula a velocidade simulada (entre 40 e 80 km/h)
        speed = random.uniform(40, 80)
        
        # Calcula o heading (direção) com base nas coordenadas atuais e próximas
        heading = 0
        if i < len(ROUTE_COORDINATES) - 1:
            next_coord = ROUTE_COORDINATES[i + 1]
            # Cálculo simplificado do heading
            heading = random.uniform(0, 359)
        
        # Cria a mensagem de atualização de localização
        message = {
            "type": "location_update",
            "latitude": coord["lat"],
            "longitude": coord["lng"],
            "accuracy": random.uniform(3, 10),  # Precisão entre 3 e 10 metros
            "speed": speed,
            "heading": heading
        }
        
        # Envia a mensagem
        await websocket.send(json.dumps(message))
        print(f"[{datetime.now().isoformat()}] Enviada atualização de localização: {message}")
        
        # Aguarda a resposta
        response = await websocket.recv()
        print(f"[{datetime.now().isoformat()}] Resposta recebida: {response}")
        
        # Aguarda o intervalo especificado
        await asyncio.sleep(interval)
        
        # A cada 4 atualizações de localização, atualiza o status
        if i > 0 and i % 4 == 0 and i // 4 < len(DELIVERY_STATUSES):
            await send_status_update(websocket, delivery_id, DELIVERY_STATUSES[i // 4])

async def send_status_update(websocket, delivery_id, status):
    """Envia uma atualização de status para o servidor."""
    message = {
        "type": "status_update",
        "status": status,
        "notes": f"Status atualizado para {status} em {datetime.now().isoformat()}"
    }
    
    # Envia a mensagem
    await websocket.send(json.dumps(message))
    print(f"[{datetime.now().isoformat()}] Enviada atualização de status: {message}")
    
    # Aguarda a resposta
    response = await websocket.recv()
    print(f"[{datetime.now().isoformat()}] Resposta recebida: {response}")

async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Cliente WebSocket para testar o rastreamento de entregas.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host do servidor")
    parser.add_argument("--port", default=DEFAULT_PORT, help="Porta do servidor")
    parser.add_argument("--delivery-id", default=DEFAULT_DELIVERY_ID, help="ID da entrega")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Token JWT")
    parser.add_argument("--username", help="Nome de usuário para obter token")
    parser.add_argument("--password", help="Senha para obter token")
    parser.add_argument("--interval", type=int, default=5, help="Intervalo entre atualizações (segundos)")
    
    args = parser.parse_args()
    
    # Verifica se temos um token ou credenciais para obter um
    token = args.token
    if not token and args.username and args.password:
        token = await get_token(args.host, args.port, args.username, args.password)
        if not token:
            print("Não foi possível obter um token. Verifique suas credenciais.")
            return
    
    if not token:
        print("É necessário fornecer um token JWT ou credenciais para obter um.")
        return
    
    if not args.delivery_id:
        print("É necessário fornecer um ID de entrega.")
        return
    
    # URL do WebSocket
    ws_url = f"ws://{args.host}:{args.port}/ws/delivery/tracking/{args.delivery_id}/"
    
    # Cabeçalhos com o token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Conecta ao WebSocket
        async with websockets.connect(ws_url, extra_headers=headers) as websocket:
            print(f"Conectado ao WebSocket: {ws_url}")
            
            # Recebe a mensagem inicial (localização atual)
            initial_message = await websocket.recv()
            print(f"Mensagem inicial recebida: {initial_message}")
            
            # Envia atualizações de localização
            await send_location_updates(websocket, args.delivery_id, args.interval)
    
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
