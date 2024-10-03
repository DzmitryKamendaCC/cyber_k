from fastapi import FastAPI, Request, HTTPException, Depends
import sqlite3
import argparse
import uvicorn
import configparser

# Sukuriamas FastAPI programos objektas
app = FastAPI()

def read_config(config_path="config.ini"):
    """Nuskaito konfigūracijos failą ir grąžina reikšmes."""
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        # Nuskaitomos reikšmės iš atitinkamų sekcijų
        db_file = config.get('second_service', 'db_file', fallback="events.db")
        return db_file
    except configparser.Error as e:
        print(f"Klaida skaitant konfigūracijos failą: {e}")
        return "events.db"



@app.post("/event")
async def save_event(request: Request, db_file: str = Depends(read_config)):  
    """Išsaugo įvykį duomenų bazėje.

    Args:
        request: Užklausa su įvykio duomenimis.
        db_file (str): Duomenų bazės failo kelias.

    Returns:
        Pranešimas, kad įvykis išsaugotas.

    Gauna įvykį ir išsaugo jį duomenų bazėje.
    Jei įvykio formatas netinkamas, grąžina klaidą.
    """
    try:
        # Gauna įvykio duomenis iš užklausos
        event = await request.json()

        # Patikrina, ar įvykis yra tinkamo formato (žodynas su reikiamais raktais)
        if not isinstance(event, dict) or "event_type" not in event or "event_payload" not in event:
            # grąžina klaidos pranešimą, jei neatitinka
            raise HTTPException(status_code=400, detail="Netinkamas įvykio formatas")

        # Prisijungia prie duomenų bazės
        conn = sqlite3.connect(db_file)  # Naudojamas db_file argumentas
        cur = conn.cursor()

        # Sukuria lentelę, jei jos dar nėra
        cur.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_payload TEXT NOT NULL
            )
        ''')

        # Įterpia įvykio duomenis į lentelę
        cur.execute("INSERT INTO events (event_type, event_payload) VALUES (?, ?)", (event["event_type"], event["event_payload"]))

        # Išsaugo pakeitimus duomenų bazėje ir uždaro ryšį su duomenų baze
        conn.commit()
        cur.close()
        conn.close()

        # Grąžina pranešimą, kad įvykis išsaugotas
        return {"message": "Įvykis sėkmingai išsaugotas!"}
    # Jei įvyko klaida, grąžina klaidos pranešimą
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """
    Nuskaito konfigūracijos parametrus ir paleidžia serverį.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Paleidžiamas serveris
    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()