import os
from pathlib import Path
from tkinter import (
    Tk,
    Button,
    Label,
    StringVar,
    filedialog,
    messagebox,
)
from tkinter.ttk import Progressbar

from PIL import Image


class ConvertisseurJPEGPNG:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Convertisseur JPEG vers PNG")
        self.root.geometry("600x250")
        self.root.resizable(False, False)

        self.dossier_selectionne = StringVar(value="Aucun dossier sélectionné")
        self.status = StringVar(value="Sélectionnez un dossier contenant des images JPEG.")

        self._build_ui()

    def _build_ui(self) -> None:
        # Titre
        titre = Label(
            self.root,
            text="Convertisseur JPEG → PNG",
            font=("Segoe UI", 16, "bold"),
        )
        titre.pack(pady=(15, 5))

        # Dossier sélectionné
        label_dossier = Label(
            self.root,
            textvariable=self.dossier_selectionne,
            font=("Segoe UI", 9),
            wraplength=560,
            justify="center",
        )
        label_dossier.pack(pady=(0, 10))

        # Boutons
        frame_btns = __import__("tkinter").Frame(self.root)
        frame_btns.pack(pady=5)

        btn_choisir = Button(
            frame_btns,
            text="Choisir un dossier...",
            font=("Segoe UI", 10),
            command=self.choisir_dossier,
            width=18,
        )
        btn_choisir.grid(row=0, column=0, padx=5)

        self.btn_convertir = Button(
            frame_btns,
            text="Convertir et supprimer les JPEG",
            font=("Segoe UI", 10, "bold"),
            command=self.convertir,
            width=28,
            state="disabled",
        )
        self.btn_convertir.grid(row=0, column=1, padx=5)

        # Barre de progression
        self.progress = Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=(15, 5))

        # Label de statut
        label_status = Label(
            self.root,
            textvariable=self.status,
            font=("Segoe UI", 9),
            wraplength=560,
            justify="center",
        )
        label_status.pack(pady=(0, 10))

    def choisir_dossier(self) -> None:
        dossier = filedialog.askdirectory(title="Choisissez un dossier contenant des JPEG")
        if not dossier:
            return

        self.dossier = Path(dossier)
        self.dossier_selectionne.set(f"Dossier : {self.dossier}")
        self.status.set("Dossier sélectionné. Cliquez sur « Convertir et supprimer les JPEG » pour commencer.")
        self.btn_convertir.config(state="normal")

    def _trouver_images_jpeg(self) -> list[Path]:
        jpeg_ext = {".jpg", ".jpeg", ".JPG", ".JPEG"}
        fichiers = []
        for racine, _, noms_fichiers in os.walk(self.dossier):
            for nom in noms_fichiers:
                chemin = Path(racine) / nom
                if chemin.suffix in jpeg_ext:
                    fichiers.append(chemin)
        return fichiers

    def convertir(self) -> None:
        if not hasattr(self, "dossier") or not self.dossier.exists():
            messagebox.showerror("Erreur", "Aucun dossier valide sélectionné.")
            return

        fichiers = self._trouver_images_jpeg()
        if not fichiers:
            messagebox.showinfo("Aucune image", "Aucune image JPEG trouvée dans ce dossier.")
            return

        total = len(fichiers)
        self.progress["value"] = 0
        self.progress["maximum"] = total
        self.status.set(f"{total} image(s) trouvée(s). Conversion en cours...")
        self.btn_convertir.config(state="disabled")
        self.root.update_idletasks()

        converties = 0
        erreurs = 0

        for i, chemin_jpeg in enumerate(fichiers, start=1):
            try:
                # Calcul du chemin PNG
                png_path = chemin_jpeg.with_suffix(".png")

                # Ouverture et conversion
                with Image.open(chemin_jpeg) as img:
                    img = img.convert("RGBA")
                    img.save(png_path, "PNG")

                # Suppression du JPEG original
                chemin_jpeg.unlink(missing_ok=True)
                converties += 1
            except Exception as e:  # noqa: BLE001
                print(f"Erreur sur {chemin_jpeg}: {e}")
                erreurs += 1

            self.progress["value"] = i
            self.status.set(f"Conversion en cours... ({i}/{total})")
            self.root.update_idletasks()

        # Résumé
        message = f"Conversion terminée.\n\nImages converties : {converties}"
        if erreurs:
            message += f"\nErreurs : {erreurs} (voir la console)"

        self.status.set("Conversion terminée.")
        messagebox.showinfo("Terminé", message)
        self.btn_convertir.config(state="normal")


def main() -> None:
    root = Tk()
    app = ConvertisseurJPEGPNG(root)
    root.mainloop()


if __name__ == "__main__":
    main()

