/**
 * DIP Practical - Quiz System
 * Handles pre-built quizzes (HTML-based quiz-question elements).
 */
(function () {
    'use strict';

    var createEl = function (tag, className, textContent) {
        var el = document.createElement(tag);
        if (className) el.className = className;
        if (textContent !== undefined && textContent !== null) el.textContent = textContent;
        return el;
    };

    function showQuizResult(quizContainer, score, total) {
        var resultDiv = createEl('div', 'quiz-final-result');
        resultDiv.style.marginTop = '1.5rem';
        resultDiv.style.padding = '1.5rem';
        resultDiv.style.borderRadius = '8px';
        resultDiv.style.textAlign = 'center';

        var pct = Math.round((score / total) * 100);
        var grade;
        if (pct >= 90) {
            grade = 'Excellent!';
            resultDiv.style.backgroundColor = '#c8e6c9';
            resultDiv.style.borderLeft = '4px solid #2e7d32';
        } else if (pct >= 70) {
            grade = 'Good job!';
            resultDiv.style.backgroundColor = '#fff9c4';
            resultDiv.style.borderLeft = '4px solid #f9a825';
        } else if (pct >= 50) {
            grade = 'Keep studying!';
            resultDiv.style.backgroundColor = '#ffe0b2';
            resultDiv.style.borderLeft = '4px solid #ef6c00';
        } else {
            grade = 'Review the material.';
            resultDiv.style.backgroundColor = '#ffcdd2';
            resultDiv.style.borderLeft = '4px solid #c62828';
        }

        var resultTitle = createEl('h4', 'quiz-result-title', 'Quiz Complete!');
        resultTitle.style.marginBottom = '0.5rem';
        resultDiv.appendChild(resultTitle);

        var resultScore = createEl('div', 'quiz-result-score', score + ' / ' + total + ' (' + pct + '%)');
        resultScore.style.fontSize = '1.3rem';
        resultScore.style.fontWeight = '700';
        resultScore.style.marginBottom = '0.5rem';
        resultDiv.appendChild(resultScore);

        var resultGrade = createEl('div', 'quiz-result-grade', grade);
        resultGrade.style.fontSize = '1.1rem';
        resultDiv.appendChild(resultGrade);

        quizContainer.appendChild(resultDiv);
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function initPrebuiltQuizzes() {
        var quizContainers = document.querySelectorAll('.quiz-container');
        quizContainers.forEach(function (quizContainer) {
            var questions = quizContainer.querySelectorAll('.quiz-question');
            if (questions.length === 0) return;

            var totalQuestions = questions.length;
            var score = 0;
            var answered = 0;

            var scoreDisplay = createEl('div', 'quiz-score');
            var scoreText = createEl('span', 'quiz-score-text', 'Score: 0 / ' + totalQuestions);
            scoreDisplay.appendChild(scoreText);
            var progressBar = createEl('div', 'quiz-progress-bar');
            progressBar.style.height = '6px';
            progressBar.style.backgroundColor = '#e2e8f0';
            progressBar.style.borderRadius = '3px';
            progressBar.style.overflow = 'hidden';
            progressBar.style.marginTop = '6px';
            var progressFill = createEl('div', 'quiz-progress-fill');
            progressFill.style.height = '100%';
            progressFill.style.width = '0%';
            progressFill.style.backgroundColor = '#10b981';
            progressFill.style.transition = 'width 0.4s ease, background-color 0.4s ease';
            progressBar.appendChild(progressFill);
            scoreDisplay.appendChild(progressBar);

            if (quizContainer.firstChild) {
                quizContainer.insertBefore(scoreDisplay, quizContainer.firstChild);
            } else {
                quizContainer.appendChild(scoreDisplay);
            }

            questions.forEach(function (questionEl) {
                var options = questionEl.querySelectorAll('.quiz-option');
                var explanationEl = questionEl.querySelector('.quiz-explanation');
                var correctIndex = parseInt(questionEl.dataset.correct, 10);
                var isAnswered = false;

                options.forEach(function (option) {
                    option.addEventListener('click', function () {
                        if (isAnswered) return;
                        isAnswered = true;
                        answered++;

                        var optIndex = parseInt(option.dataset.index, 10);
                        var isCorrect = optIndex === correctIndex;

                        if (isCorrect) {
                            score++;
                            option.classList.add('quiz-option-correct');
                        } else {
                            option.classList.add('quiz-option-wrong');
                            options.forEach(function (opt) {
                                if (parseInt(opt.dataset.index, 10) === correctIndex) {
                                    opt.classList.add('quiz-option-correct');
                                }
                            });
                        }

                        options.forEach(function (opt) {
                            opt.classList.add('quiz-option-disabled');
                        });

                        if (explanationEl) {
                            explanationEl.style.display = 'block';
                        }

                        scoreText.textContent = 'Score: ' + score + ' / ' + totalQuestions;
                        progressFill.style.width = ((answered / totalQuestions) * 100) + '%';
                        progressFill.style.backgroundColor = score === answered ? '#10b981' : '#f59e0b';

                        if (answered === totalQuestions) {
                            showQuizResult(quizContainer, score, totalQuestions);
                        }
                    });
                });
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPrebuiltQuizzes);
    } else {
        initPrebuiltQuizzes();
    }
})();
