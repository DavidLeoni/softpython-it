# Guida per contributors


SoftPython vuole essere un libro per umani, quindi:

- Dare del tu al lettore, quindi preferire _scrivi_ a _scrivete_ 
- Quando possibile inventare storielle, variando i temi (pirati, cowboy, etc), aumentano incredibilmente l'attenzione e partecipazione degli studenti. 
- Usare nomi in italiano per le variabili, evitare nomi astratti tipo `x`, per es `monete` è molto meglio
- Se si ha voglia, fare disegni / schemi in SVG con Inkscape ed esportarli in png (fornire entrambi)
- Per ogni comando che si usa, accertarsi sempre che sia stato definito precedentemente nel libro. Tenere ridotto il numero di metodi diversi da usare negli esercizi

Nei primi fogli dei fondamenti (1,2,3..):

- non usare iterazione, definizione di funzioni, assert
- deve essere sempre chiaro se del codice produce un risultato (eventualmente da stampare) oppure MODIFICA l'input. 
- quando possibile mettere gli input su una sola linea seguiti dal risultato atteso commentato, aggiungendo  almeno un'altro caso di test commentato tipo:

```python
vel=23; km=48    # True
# vel=15; km=39  # False
# vel=18; km=22  # False
```

Nelle sezioni più avanzate (es matrici):

- testare sempre con gli `assert` (al momento non sono comodi da testare a mano, un giorno mi deciderò a scrivere una funzioncina che lanci automaticamente pytest)
- evitare codice che richieda di stampare
- Se è una funzione, specificare chiaramente se RITORNA un risultato o MODIFICA l'input.  Evitare funzioni che facciano entrambe le cose. Evitare funzioni che stampano, a meno che non abbiano davvero senso (es: print log di simulazione)

## Editing

Ci sono una serie di comandi per ricavare automaticamente il testo degli esercizi a partire dalle soluzioni, li trovate nella pagina [Jupman: Usage](https://jupman.softpython.org/en/latest/usage.html#Solution-tags) 
    - nota: per l'edizione italiana `# write here` diventa  `# scrivi qui` e `# SOLUTION` diventa `# SOLUZIONE`
    - NOTA: i comandi purge rimuovono il testo sia dall'esercizio che dalla soluzione presenti negli zip, quindi i comandi li 
troverete solo nell'ipynb originale su Github


## Formattazione

- Quando si scrivono termini di Python o variabili, usare il backquote per evidenziarli, tipo `True`, `anni`
- Nelle `print` se possibile preferire la virgola  es `print("Hai fatto", salti, "salti")` a formattazione / concatenazione.
- per la formattazione delle stringhe, usare i `%` tipo `"Hai fatto %s " % salti`. Non usare f-string. Evitare concatenzioni tipo `"fai " + str(n) + " salti"`

# Altro

- evitare codice con `input` da utente (è difficile e noioso da testare, può andar bene per fare giochi)
- inclusività maschile/femminile: quando in dubbio, usare il criterio stocastico e tirare una moneta, croce usare maschile testa usare femminile, distribuendo equamente. Evitare forme intermedie tipo *, ə.

