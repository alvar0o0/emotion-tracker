# 🚀 Checklist: Validación PR Jules (Modelo Ekman)

## 1. Sincronización en el BMAX
Indispensable para que tu servidor local reconozca el trabajo de Jules en GitHub.
- [ ] `git fetch origin` (Actualizar referencias remotas)
- [ ] `git checkout feature/ekman-model` (Saltar a la rama del PR)
- [ ] `git pull origin feature/ekman-model` (Asegurar que tienes el último commit de Jules)

---

## 2. Entorno y Dependencias
Evita errores de "ModuleNotFoundError" por cambios en la arquitectura.
- [ ] Activar entorno: `source venv/bin/activate`
- [ ] Actualizar paquetes:
```bash
pip install -r backend/requirements.txt
pip install -r telegram_bot/requirements.txt
pip install -r cli/requirements.txt
```

---

## 3. Pruebas de Integración (Tmux Workflow)
Valida que el "corazón" y los "brazos" del proyecto sigan coordinados.
- [ ] **Backend:** `cd backend && uvicorn main:app --port 8000 --reload`
    - [ ] ¿Carga sin errores de importación desde `shared/`?
- [ ] **CLI:** `python cli/cli.py log`
    - [ ] ¿Muestra las 6 emociones de Ekman (Alegría, Tristeza, etc.)?
- [ ] **Telegram Bot:** `/start` en el celular.
    - [ ] ¿El bot responde y reconoce los nuevos emojis?

---

## 4. Code Review en LazyVim
Revisión rápida de la calidad del código antes del merge final.
- [ ] **Rutas:** Verificar que el archivo de constantes en `shared/` se importe correctamente.
- [ ] **Logs:** Confirmar que no haya `print()` perdidos y se use el `logger`.
- [ ] **DB:** Verificar que los nuevos nombres de emociones se guarden correctamente en la SQLite.

---

## 5. Merge y Limpieza (Ruta Hacker)
Una vez validado, dejamos el repo impecable.
- [ ] Hacer **Merge** en la interfaz de GitHub.
- [ ] Volver a main: `git checkout main`
- [ ] Sincronizar: `git pull origin main`
- [ ] Borrar rama local: `git branch -d feature/ekman-model`
