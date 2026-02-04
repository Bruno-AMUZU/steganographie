from pathlib import Path
from tkinter import (
    Tk,
    Label,
    Button,
    Entry,
    StringVar,
    filedialog,
    messagebox,
)
from PIL import Image

from code_accompagnement import cacher_message, message_to_bin


class SteganoApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Stéganographie – cacher un message dans une image")
        self.root.geometry("600x250")
        self.root.resizable(False, False)

        self.image_selectionnee = StringVar(value="Aucune image sélectionnée")
        self.status = StringVar(
            value="Sélectionnez une image PNG/JPEG puis saisissez un message."
        )
        self.message_var = StringVar(value="")

        self.image_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Titre
        titre = Label(
            self.root,
            text="Stéganographie – cacher un message dans une image",
            font=("Segoe UI", 14, "bold"),
        )
        titre.pack(pady=(15, 5))

        # Image sélectionnée
        label_image = Label(
            self.root,
            textvariable=self.image_selectionnee,
            font=("Segoe UI", 9),
            wraplength=560,
            justify="center",
        )
        label_image.pack(pady=(0, 10))

        # Bouton pour choisir une image
        btn_choisir = Button(
            self.root,
            text="Choisir une image…",
            font=("Segoe UI", 10),
            command=self.choisir_image,
            width=20,
        )
        btn_choisir.pack(pady=(0, 10))

        # Zone de saisie du message
        label_message = Label(
            self.root,
            text="Message à cacher :",
            font=("Segoe UI", 10),
        )
        label_message.pack()

        entry_message = Entry(
            self.root,
            textvariable=self.message_var,
            font=("Segoe UI", 10),
            width=60,
        )
        entry_message.pack(pady=(0, 10))

        # Bouton d'action
        btn_cacher = Button(
            self.root,
            text="Cacher le message",
            font=("Segoe UI", 10, "bold"),
            command=self.cacher_message_dans_image,
            width=20,
        )
        btn_cacher.pack(pady=(0, 10))

        # Label de statut
        label_status = Label(
            self.root,
            textvariable=self.status,
            font=("Segoe UI", 9),
            wraplength=560,
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

        self.image_path = Path(fichier)
        self.image_selectionnee.set(f"Image : {self.image_path}")
        self.status.set("Image sélectionnée. Saisissez un message puis cliquez sur « Cacher le message ».")

    def _message_tient_dans_image(self, image_path: Path, message: str) -> bool:
        # Calcule si le nombre de bits nécessaires est <= nombre de pixels
        bits_message = message_to_bin(message) + "1111111111111110"
        nb_bits = len(bits_message)

        with Image.open(image_path) as img:
            largeur, hauteur = img.size

        capacite = largeur * hauteur  # 1 bit par pixel (canal Rouge)
        return nb_bits <= capacite

    def cacher_message_dans_image(self) -> None:
        if self.image_path is None or not self.image_path.exists():
            messagebox.showerror("Erreur", "Aucune image valide sélectionnée.")
            return

        message = self.message_var.get()
        if not message:
            messagebox.showerror("Erreur", "Veuillez saisir un message à cacher.")
            return

        # Vérification simple de capacité
        if not self._message_tient_dans_image(self.image_path, message):
            messagebox.showerror(
                "Message trop long",
                "Votre message est trop long pour être caché dans cette image.\n"
                "Choisissez une image plus grande ou raccourcissez le message.",
            )
            return

        # Nom du fichier de sortie : même nom + suffixe _codee.png
        base = self.image_path.with_suffix("")  # enlève l'extension
        image_codee_path = base.with_name(base.name + "_codee").with_suffix(".png")

        try:
            cacher_message(str(self.image_path), message, str(image_codee_path))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors du codage du message :\n{e}",
            )
            self.status.set("Erreur lors du codage du message.")
            return

        messagebox.showinfo(
            "Succès",
            f"Message caché dans l'image :\n{image_codee_path}",
        )
        self.status.set(f"Message caché avec succès dans {image_codee_path}.")


def main() -> None:
    root = Tk()
    app = SteganoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()