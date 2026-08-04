from agents import function_tool

book_summaries_dict = {
    "1984": (
        "Romanul lui George Orwell descrie o societate distopică aflată sub "
        "controlul total al statului. Oamenii sunt supravegheați permanent de "
        "Big Brother, iar libertatea de gândire este considerată o crimă. "
        "Winston Smith începe să se îndoiască de regim și încearcă să descopere "
        "adevărul. Cartea explorează teme precum libertatea, propaganda, "
        "supravegherea și manipularea."
    ),

    "The Hobbit": (
        "Bilbo Baggins este un hobbit liniștit care este atras într-o aventură "
        "alături de un grup de pitici și vrăjitorul Gandalf. Misiunea lor este "
        "să recupereze comoara păzită de dragonul Smaug. Pe parcurs, Bilbo își "
        "descoperă curajul și inteligența. Cartea explorează aventura, prietenia, "
        "curajul și lumea fantastică."
    ),

    "The Lord of the Rings": (
        "Frodo Baggins primește misiunea de a distruge un inel extrem de puternic "
        "care poate aduce întreaga lume sub controlul lui Sauron. El pornește "
        "într-o călătorie periculoasă alături de prieteni și aliați. Povestea "
        "prezintă lupta dintre bine și rău, sacrificiul, loialitatea și speranța."
    ),

    "Harry Potter and the Philosopher's Stone": (
        "Harry Potter descoperă că este vrăjitor și începe să studieze la Hogwarts. "
        "Acolo își face prieteni, învață magie și descoperă adevărul despre trecutul "
        "său. Împreună cu Ron și Hermione, investighează un mister ascuns în școală. "
        "Cartea are ca teme principale prietenia, magia, curajul și descoperirea de sine."
    ),

    "The Book Thief": (
        "Povestea urmărește viața unei fete pe nume Liesel în Germania nazistă. "
        "Ea descoperă puterea cărților și a cuvintelor într-o perioadă dominată "
        "de război și teamă. Familia ei ascunde un evreu, punându-și viața în pericol. "
        "Romanul explorează umanitatea, pierderea, războiul și puterea poveștilor."
    ),

    "To Kill a Mockingbird": (
        "Scout Finch crește într-un mic oraș american și observă nedreptățile "
        "societății din jurul său. Tatăl ei, avocatul Atticus Finch, apără un bărbat "
        "acuzat pe nedrept. Cartea tratează teme precum rasismul, justiția, empatia "
        "și maturizarea."
    ),

    "The Alchemist": (
        "Santiago, un tânăr păstor, pornește într-o călătorie pentru a găsi o comoară. "
        "Pe drum întâlnește oameni care îl ajută să își înțeleagă visele și scopul. "
        "Călătoria devine una de autodescoperire. Cartea explorează destinul, curajul, "
        "speranța și urmarea propriilor visuri."
    ),

    "The Little Prince": (
        "Un pilot întâlnește în deșert un prinț venit de pe o planetă îndepărtată. "
        "Prințul îi povestește despre călătoriile sale și despre oamenii pe care "
        "i-a cunoscut. Povestea vorbește despre prietenie, iubire, singurătate și "
        "modul în care adulții uită lucrurile cu adevărat importante."
    ),

    "Fahrenheit 451": (
        "Într-o societate în care cărțile sunt interzise, pompierii au rolul de a le arde. "
        "Guy Montag începe să se întrebe de ce cărțile sunt considerate periculoase. "
        "El ajunge să conteste sistemul și să caute cunoașterea. Romanul explorează "
        "cenzura, conformismul, libertatea și controlul informației."
    ),

    "Pride and Prejudice": (
        "Elizabeth Bennet îl întâlnește pe domnul Darcy, un bărbat bogat și aparent "
        "arogant. Relația lor este influențată de prejudecăți, orgoliu și diferențe "
        "sociale. Pe măsură ce se cunosc mai bine, amândoi își schimbă percepțiile. "
        "Romanul explorează iubirea, familia, statutul social și maturizarea."
    ),

    "All Quiet on the Western Front": (
        "Un grup de tineri germani se înrolează în armată în timpul Primului Război "
        "Mondial. Ei descoperă rapid realitatea brutală a frontului. Experiențele lor "
        "arată pierderea inocenței și efectele psihologice ale războiului. Cartea "
        "explorează camaraderia, trauma, supraviețuirea și absurditatea războiului."
    ),

    "The Chronicles of Narnia": (
        "Mai mulți copii descoperă o lume magică numită Narnia, populată de animale "
        "vorbitoare și creaturi fantastice. Ei sunt implicați într-o luptă dintre bine "
        "și rău. Cu ajutorul leului Aslan, copiii învață despre curaj și responsabilitate. "
        "Temele principale sunt magia, aventura, sacrificiul și prietenia."
    ),
}

@function_tool
def get_summary_by_title(title: str) -> str:
    """
    Returnează rezumatul complet al unei cărți după titlu.

    Args: Titlul cartii cautate.
    """

    normalized_title = title.strip().lower()

    for book_title, summary in book_summaries_dict.items():
        if book_title.lower() == normalized_title:
            return (
                f"Titlul cărții: '{book_title}'\n"
                f"Rezumatul complet: {summary}"

            )

    available_titles = ", ".join(book_summaries_dict.keys())

    return (
        f"Nu am găsit cartea '{title}'. "
        f"Titlurile disponibile sunt: {available_titles}."
    )


