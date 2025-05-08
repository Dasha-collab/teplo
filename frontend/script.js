document.addEventListener('DOMContentLoaded', () => {
  const uploadArea = document.getElementById('upload-area');
  const fileInput = document.getElementById('upload');
  const analyzeBtn = document.getElementById('analyze-btn');
  const resultDiv = document.getElementById('result');
  const downloadBtn = document.getElementById('download');

  // Обработка выбора файла
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        document.getElementById('preview').src = e.target.result;
      };
      reader.readAsDataURL(file);
      analyzeBtn.disabled = false;
    }
  });

  // Анализ изображения
  analyzeBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    // Показать загрузку
    analyzeBtn.disabled = true;
    document.getElementById('spinner').style.display = 'block';
    resultDiv.textContent = '';
    downloadBtn.style.display = 'none';

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('https://teplo.onrender.com/analyze/', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Ошибка сервера' }));
        throw new Error(error.detail);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      downloadBtn.href = url;
      downloadBtn.style.display = 'block';
      resultDiv.textContent = 'Анализ завершён!';
    } catch (error) {
      resultDiv.textContent = `Ошибка: ${error.message}`;
      resultDiv.classList.add('error');
    } finally {
      analyzeBtn.disabled = false;
      document.getElementById('spinner').style.display = 'none';
    }
  });
});
