#!/usr/bin/env python3
import argparse
import random
import string
import sys
import textwrap

# =============================
#   COULEURS ANSI
# =============================

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"

def colorize(text, color_enabled=True, color_code=COLOR_GREEN):
    if not color_enabled:
        return text
    return f"{color_code}{text}{COLOR_RESET}"


# =============================
#   MANUEL TYPE "man pwgen"
# =============================

MAN_PAGE = """
PWGEN(1)                     User Commands                    PWGEN(1)

NAME
       pwgen - générateur de mots de passe en Python inspiré de pwgen

SYNOPSIS
       pwgen [OPTIONS] [length] [count]

DESCRIPTION
       Ce programme génère des mots de passe aléatoires ou prononçables,
       avec des options similaires à la commande pwgen originale.
       Il propose également :
         - un mode interactif,
         - la génération de passphrases type diceware,
         - la coloration ANSI de la sortie.

OPTIONS
       -c, --capitalize
              Inclure au moins une majuscule dans chaque mot de passe.

       -n, --numerals
              Inclure au moins un chiffre.

       -y, --symbols
              Inclure des symboles.

       -s, --secure
              Mode sécurisé : force l'utilisation de majuscules,
              minuscules, chiffres, symboles et exclut les caractères
              ambigus.

       -B, --no-ambiguous
              Exclut les caractères ambigus (0, O, 1, l, I).

       -A, --no-capitalize
              Désactive les majuscules.

       -N, --no-numerals
              Désactive les chiffres.

       -Y, --no-symbols
              Désactive les symboles.

       -p, --pronounceable
              Génère des mots de passe prononçables.

       -i, --interactive
              Mode interactif : pose des questions à l'utilisateur.

       -d, --diceware
              Génère une passphrase type diceware au lieu d'un mot de passe.

       --dice-words N
              Nombre de mots dans la passphrase diceware (par défaut 6).

       --no-color
              Désactive les couleurs ANSI dans la sortie.

       --man
              Affiche cette page de manuel.

EXAMPLES
       pwgen 16 5
              Génère 5 mots de passe de 16 caractères.

       pwgen -s 20
              Génère un mot de passe sécurisé de 20 caractères.

       pwgen -d --dice-words 7
              Génère une passphrase diceware de 7 mots.

       pwgen -i
              Lance le mode interactif.

AUTHOR
       ZANDARIN Nicolas.

"""


# =============================
#   DICEWARE : WORDLIST SIMPLE
# =============================
# NOTE : pour un usage réel, remplace cette liste par
# une vraie wordlist diceware (eff.org, etc.).
DICEWARE_WORDLIST = [
    "chat", "lune", "rouge", "forêt", "porte", "verre", "bleu",
    "code", "python", "neige", "pierre", "rivière", "nuit", "feuille",
    "soleil", "orage", "clé", "étoile", "table", "verre"
]

def generate_diceware(num_words=6, separator="-"):
    words = [random.choice(DICEWARE_WORDLIST) for _ in range(num_words)]
    return separator.join(words)


# =============================
#   GÉNÉRATEUR DE MOTS DE PASSE
# =============================

AMBIGUOUS = "Il1O0"

def generate_pronounceable(length):
    vowels = "aeiou"
    consonants = "".join(c for c in string.ascii_lowercase if c not in vowels)
    pwd = ""
    for i in range(length):
        if i % 2 == 0:
            pwd += random.choice(consonants)
        else:
            pwd += random.choice(vowels)
    return pwd


def generate_password(length, opts):
    if opts.diceware:
        return generate_diceware(num_words=opts.dice_words)

    chars = ""

    if opts.lowercase:
        chars += string.ascii_lowercase
    if opts.uppercase:
        chars += string.ascii_uppercase
    if opts.numerals:
        chars += string.digits
    if opts.symbols:
        chars += "!@#$%^&*()-_=+[]{};:,.?/"

    if opts.no_ambiguous:
        chars = ''.join(c for c in chars if c not in AMBIGUOUS)

    if opts.pronounceable:
        return generate_pronounceable(length)

    if not chars:
        raise ValueError("Aucun jeu de caractères disponible.")

    # Génération brute
    pwd = ''.join(random.choice(chars) for _ in range(length))

    # Contraintes minimales
    if opts.uppercase and not any(c.isupper() for c in pwd):
        pwd = pwd[:-1] + random.choice(string.ascii_uppercase)
    if opts.numerals and not any(c.isdigit() for c in pwd):
        pwd = pwd[:-1] + random.choice(string.digits)
    if opts.symbols and not any(c in "!@#$%^&*()-_=+[]{};:,.?/" for c in pwd):
        pwd = pwd[:-1] + random.choice("!@#$%^&*()-_=+[]{};:,.?/")

    return pwd


# =============================
#   MODE SECURE
# =============================

def apply_secure_mode(opts):
    opts.uppercase = True
    opts.lowercase = True
    opts.numerals = True
    opts.symbols = True
    opts.no_ambiguous = True
    opts.pronounceable = False
    opts.diceware = False


# =============================
#   MODE INTERACTIF
# =============================

def interactive_mode(opts):
    print(colorize("=== Mode interactif pwgen ===", opts.color, COLOR_CYAN))

    # Type : password ou diceware
    mode = input("Générer un (p)assword ou une passphrase (d)iceware ? [p/d] (p) : ").strip().lower()
    if mode == "d":
        opts.diceware = True
        try:
            n = input("Nombre de mots dans la passphrase (défaut 6) : ").strip()
            if n:
                opts.dice_words = int(n)
        except ValueError:
            print("Valeur invalide, utilisation de 6 mots.")
            opts.dice_words = 6
        # length n'est pas pertinent pour diceware, on ignore
    else:
        opts.diceware = False
        # Longueur
        try:
            length = input(f"Longueur du mot de passe (défaut {opts.length}) : ").strip()
            if length:
                opts.length = int(length)
        except ValueError:
            print("Valeur invalide, utilisation de la longueur par défaut.")

    # Nombre de mots de passe
    try:
        count = input(f"Nombre à générer (défaut {opts.count}) : ").strip()
        if count:
            opts.count = int(count)
    except ValueError:
        print("Valeur invalide, utilisation du count par défaut.")

    # Secure ?
    secure = input("Mode sécurisé ? [o/N] : ").strip().lower()
    if secure == "o":
        apply_secure_mode(opts)
    else:
        # Options fines (si non diceware)
        if not opts.diceware:
            capital = input("Inclure des majuscules ? [O/n] : ").strip().lower()
            if capital == "n":
                opts.uppercase = False
            else:
                opts.uppercase = True

            numerals = input("Inclure des chiffres ? [O/n] : ").strip().lower()
            if numerals == "n":
                opts.numerals = False
            else:
                opts.numerals = True

            symbols = input("Inclure des symboles ? [o/N] : ").strip().lower()
            if symbols == "o":
                opts.symbols = True
            else:
                opts.symbols = False

            ambig = input("Exclure les caractères ambigus ? [o/N] : ").strip().lower()
            if ambig == "o":
                opts.no_ambiguous = True
            else:
                opts.no_ambiguous = False

            pronounce = input("Mode prononçable ? [o/N] : ").strip().lower()
            if pronounce == "o":
                opts.pronounceable = True
            else:
                opts.pronounceable = False

    print()  # ligne vide esthétique
    return opts


# =============================
#   CLI
# =============================

def build_parser():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("length", nargs="?", type=int, default=12)
    parser.add_argument("count", nargs="?", type=int, default=1)

    parser.add_argument("-c", "--capitalize", action="store_true")
    parser.add_argument("-n", "--numerals", action="store_true")
    parser.add_argument("-y", "--symbols", action="store_true")
    parser.add_argument("-s", "--secure", action="store_true")
    parser.add_argument("-B", "--no-ambiguous", action="store_true")
    parser.add_argument("-A", "--no-capitalize", action="store_true")
    parser.add_argument("-N", "--no-numerals", action="store_true")
    parser.add_argument("-Y", "--no-symbols", action="store_true")
    parser.add_argument("-p", "--pronounceable", action="store_true")
    parser.add_argument("-i", "--interactive", action="store_true")
    parser.add_argument("-d", "--diceware", action="store_true")
    parser.add_argument("--dice-words", type=int, default=6)
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--man", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")

    return parser


def main():
    parser = build_parser()
    opts = parser.parse_args()

    # Gestion help / man
    if opts.help:
        print(textwrap.dedent("""
        Usage: pwgen [OPTIONS] [length] [count]

        Utilisez --man pour la page de manuel complète.
        Options principales :
          -s, --secure        Mode sécurisé
          -p, --pronounceable Mots de passe prononçables
          -d, --diceware      Passphrase façon diceware
          -i, --interactive   Mode interactif
        """).strip())
        sys.exit(0)

    if opts.man:
        print(MAN_PAGE)
        sys.exit(0)

    # Couleurs
    opts.color = not opts.no_color

    # Valeurs de base
    opts.uppercase = True
    opts.lowercase = True
    opts.numerals = True
    opts.symbols = False

    # Application des flags "no-*"
    if opts.no_capitalize:
        opts.uppercase = False
    if opts.no_numerals:
        opts.numerals = False
    if opts.no_symbols:
        opts.symbols = False

    # Application des flags positifs
    if opts.capitalize:
        opts.uppercase = True
    if opts.numerals:
        opts.numerals = True
    if opts.symbols:
        opts.symbols = True

    # Secure
    if opts.secure:
        apply_secure_mode(opts)

    # Mode interactif
    if opts.interactive:
        opts = interactive_mode(opts)

    # Génération
    try:
        for _ in range(opts.count):
            pwd = generate_password(opts.length, opts)
            print(colorize(pwd, opts.color, COLOR_GREEN))
    except ValueError as e:
        print(colorize(f"Erreur : {e}", opts.color, COLOR_RED), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
