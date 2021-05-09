function handleCharacterCount(input, modal) {
    const charCount = input.value.length;

    // Span do input da Home
    const homeSpan = document.getElementById("characterCount");

    // Span do Modal de Tweet
    const modalSpan = document.getElementById("characterCountModal");

    modal ? modalSpan.innerHTML = charCount : homeSpan.innerHTML = charCount;
}