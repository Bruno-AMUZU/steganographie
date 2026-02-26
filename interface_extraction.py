from pathlib import Path
from tkinter import (
    Tk,
    Label,
    Button,
    StringVar,
    Text,
    Scrollbar,
    END,
    filedialog,
    messagebox,
)

from PIL import Image  # juste pour vérifier rapidement qu'on ouvre bien une image

from code_accompagnement import extraire_message


class ExtractionApp:
    """Interface très simple pour extraire un message caché dans une image."""

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Stéganographie – extraire un message")
        self.root.geometry("650x300")
        self.root.resizable(False, False)

        self.image_selectionnee = StringVar(value="Aucune image sélectionnée")
        self.status = StringVar(
            value="Sélectionnez une image PNG/JPEG puis cliquez sur « Extraire le message »."
        )

        self.image_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Titre
        titre = Label(
            self.root,
            text="Stéganographie – extraire un message d’une image",
            font=("Segoe UI", 14, "bold"),
        )
        titre.pack(pady=(10, 5))

        # Image sélectionnée
        label_image = Label(
            self.root,
            textvariable=self.image_selectionnee,
            font=("Segoe UI", 9),
            wraplength=620,
            justify="center",
        )
        label_image.pack(pady=(0, 10))

        # Boutons
        btn_choisir = Button(
            self.root,
            text="Choisir une image…",
            font=("Segoe UI", 10),
            command=self.choisir_image,
            width=20,
        )
        btn_choisir.pack(pady=(0, 5))

        btn_extraire = Button(
            self.root,
            text="Extraire le message",
            font=("Segoe UI", 10, "bold"),
            command=self.extraire_message_depuis_image,
            width=20,
        )
        btn_extraire.pack(pady=(0, 10))

        # Zone de texte pour afficher le message extrait
        frame_message = __import__("tkinter").Frame(self.root)
        frame_message.pack(pady=(0, 5), fill="both", expand=False)

        label_message = Label(
            frame_message,
            text="Message extrait :",
            font=("Segoe UI", 10),
        )
        label_message.pack(anchor="w")

        scrollbar = Scrollbar(frame_message)
        scrollbar.pack(side="right", fill="y")

        self.txt_message = Text(
            frame_message,
            height=6,
            width=70,
            wrap="word",
            yscrollcommand=scrollbar.set,
        )
        self.txt_message.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.txt_message.yview)

        # Label de statut
        label_status = Label(
            self.root,
            textvariable=self.status,
            font=("Segoe UI", 9),
            wraplength=620,
            justify="center",
        )
        label_status.pack(pady=(5, 5))

    def choisir_image(self) -> None:
        fichier = filedialog.askopenfilename(
            title="Choisissez une image",
            filetypes=(
                ("Images PNG", "*.png"),
                ("Images JPEG", "*.jpg;*.jpeg;*.JPG;*.JPEG"),
                ("Tous les fichiers", "*.*"),
            ),
        )
        if not fichier:
            return

        chemin = Path(fichier)
        # Vérification rapide que c'est bien une image lisible par PIL
        try:
            with Image.open(chemin) as _:
                pass
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Erreur", f"Impossible d’ouvrir cette image :\n{e}")
            return

        self.image_path = chemin
        self.image_selectionnee.set(f"Image : {self.image_path}")
        self.status.set(
            "Image sélectionnée. Cliquez sur « Extraire le message » pour tenter de lire le code."
        )
        self.txt_message.delete("1.0", END)

    def extraire_message_depuis_image(self) -> None:
        if self.image_path is None or not self.image_path.exists():
            messagebox.showerror("Erreur", "Aucune image valide sélectionnée.")
            return

        self.status.set("Extraction en cours…")
        self.root.update_idletasks()

        try:
            message = extraire_message(str(self.image_path))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de l’extraction :\n{e}",
            )
            self.status.set("Erreur lors de l’extraction du message.")
            return

        self.txt_message.delete("1.0", END)

        if message == "Aucun marqueur de fin trouvé." or not message:
            # Cas où l'image ne contient probablement pas de message caché
            self.txt_message.insert(
                END,
                "Aucun message caché détecté dans cette image (aucun marqueur de fin trouvé).",
            )
            self.status.set(
                "Aucun message caché détecté (ou l’image n’a pas été encodée avec ce système)."
            )
        else:
            self.txt_message.insert(END, message)
            self.status.set("Message extrait avec succès.")


def main() -> None:
    root = Tk()
    app = ExtractionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

