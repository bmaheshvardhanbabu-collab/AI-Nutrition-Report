function setFood(foodName) {

    const input = document.querySelector(
        'input[name="food"]'
    );

    if (input) {

        input.value = foodName;

        input.focus();

    }

}


const foodForm = document.querySelector(
    ".food-form"
);


if (foodForm) {

    foodForm.addEventListener(
        "submit",
        function () {

            const button =
                foodForm.querySelector(
                    "button"
                );

            if (button) {

                button.innerHTML =
                    "Analyzing...";

                button.disabled = true;

            }

        }
    );

}


const questionForm = document.querySelector(
    ".question-form"
);


if (questionForm) {

    questionForm.addEventListener(
        "submit",
        function () {

            const button =
                questionForm.querySelector(
                    "button"
                );

            if (button) {

                button.innerHTML =
                    "Thinking...";

                button.disabled = true;

            }

        }
    );

}