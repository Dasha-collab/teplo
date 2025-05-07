function analyze() {
    const fileInput = document.getElementById("upload");
    const file = fileInput.files[0];
    if (!file) return alert("Выберите файл");

    const formData = new FormData();
    formData.append("file", file);

    const button = document.querySelector("button");
    button.disabled = true;
    button.textContent = "Обработка...";

    fetch("https://teplo.onrender.com/analyze/", {
        method: "POST",
        body: formData,
    })
    .then(res => {
        if (res.status === 200) return res.blob();
        return res.json().then(err => { throw new Error(err.error); });
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.getElementById("download");
        link.href = url;
        link.download = "report.pdf";
        link.style.display = "inline-block";
        link.innerText = "Скачать PDF";
    })
    .catch((err) => {
        document.getElementById("result").innerText = "Ошибка: " + err.message;
    })
    .finally(() => {
        button.disabled = false;
        button.textContent = "Анализировать";
    });
}

