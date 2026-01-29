import subprocess

async def check_ip_ping(ip):
    # Comando ping: -n 1 (un paquete), -w 200 (espera 200ms)
    comando = ["ping", "-n", "1", "-w", "200", ip]
    proceso = await asyncio.create_subprocess_exec(
        *comando,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proceso.communicate()
    
    if proceso.returncode == 0:
        print(f"ALGO RESPONDE (PING)! IP: {ip}")
        return True
    return False