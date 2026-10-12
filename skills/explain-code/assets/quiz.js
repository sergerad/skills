// Turns the static quiz markup into a self-marking quiz: shuffles each question's options, marks the
// chosen one against data-answer, and reveals the explanation. Without this script the page still
// reads as questions followed by their explanations.
(function () {
  function shuffle(list) {
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [list[i], list[j]] = [list[j], list[i]];
    }
    return list;
  }

  function setUp(quiz) {
    const questions = Array.from(quiz.querySelectorAll(".question"));
    const score = quiz.querySelector(".score");
    let answered = 0;
    let correct = 0;

    function report() {
      if (!score) return;
      score.textContent =
        answered === 0
          ? `${questions.length} questions. Pick an answer to see why it is right or wrong.`
          : `${correct} of ${answered} correct, ${questions.length - answered} to go.`;
    }

    questions.forEach((question) => {
      const list = question.querySelector(".options");
      const options = shuffle(Array.from(list.children));

      function choose(option) {
        if (question.classList.contains("answered")) return;
        question.classList.add("answered");
        const right = option.dataset.option === question.dataset.answer;
        option.classList.add(right ? "correct" : "wrong");
        options
          .filter((o) => o.dataset.option === question.dataset.answer)
          .forEach((o) => o.classList.add("correct"));
        options.forEach((o) => o.removeAttribute("tabindex"));
        answered += 1;
        if (right) correct += 1;
        report();
      }

      options.forEach((option) => {
        list.appendChild(option);
        option.setAttribute("role", "button");
        option.setAttribute("tabindex", "0");
        option.addEventListener("click", () => choose(option));
        option.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            choose(option);
          }
        });
      });
    });

    quiz.classList.add("live");
    report();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".quiz").forEach(setUp);
  });
})();
