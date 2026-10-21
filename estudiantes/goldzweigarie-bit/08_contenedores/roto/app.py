"""Lo de menos es lo que hace: el ejercicio es el Dockerfile."""
import getpass
import requests

print(f"Corriendo como: {getpass.getuser()}")
print("requests", requests.__version__)
