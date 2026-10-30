# Crittografia

Raccolta di materiale, esercizi, script e notebook sviluppati per il corso di Crittografia.

## Contenuti della cartella

### 1. Generatore di Geffe e Attacco di Correlazione
* **Notebook:** `geffe_generator.ipynb`
* **Descrizione:** 
  * **Esercizio 4.18** dal libro di testo _"Paterson e Stinson, Cryptography, Theory and Practice, Fourth edition"_: Studio analitico della funzione combinante di Geffe e calcolo delle correlazioni tra i singoli ingressi e l'uscita.
  * **Implementazione pratica:** Realizzazione in Python del generatore basato su 3 registri LFSR con tap derivati da polinomi primitivi ($4, 5$ e $6$ bit) per la cifratura e la decifratura di messaggi.
  * **Attacco:** Simulazione di un attacco di correlazione a chiaro noto per il recupero dei semi segreti senza passare per la forza bruta globale.

---

## Come utilizzare i materiali
Puoi aprire il notebook direttamente su Google Colab cliccando sul file `.ipynb` oppure eseguirlo in locale clonando il repository.
