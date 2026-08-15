const form = document.getElementById("recommend-form");
const button = document.getElementById("recommend-button");
const result = document.getElementById("recommend-result");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const date = document.getElementById("travel-date").value;
    const style = document.getElementById("travel-style").value;
    const companion = document.getElementById("travel-companion").value;
    const request = document.getElementById("travel-request").value.trim();

    // 빈 입력 확인
    if (!date || !style || !companion) {
        result.innerHTML = `
            <div class="result-error">
                <span>⚠️</span>
                <p>여행 날짜, 스타일, 동반자를 모두 선택해주세요.</p>
            </div>
        `;
        return;
    }

    // AI 요청 중 상태
    button.disabled = true;
    button.textContent = "✨ AI가 여행을 계획하고 있어요...";

    result.innerHTML = `
        <div class="result-loading">
            <span>✈️</span>
            <p>잠시만 기다려주세요.<br>여행지를 찾고 있습니다.</p>
        </div>
    `;

    try {
        const response = await fetch("/api/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                date: date,
                style: style,
                companion: companion,
                request: request
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "AI 추천을 가져오지 못했습니다."
            );
        }

        // AI 결과 표시
        result.innerHTML = `
            <div class="result-success">
                <p class="result-label">TRIPMIND AI 추천</p>

                <h3>${escapeHtml(data.recommended_city)}</h3>

                <p class="result-reason">
                    ${escapeHtml(data.reason)}
                </p>

                <div class="result-info">
                    <div>
                        <strong>🌤️ 날씨</strong>
                        <p>${escapeHtml(data.weather)}</p>
                    </div>

                    <div>
                        <strong>🎉 추천 행사</strong>
                        <ul>
                            ${
                                (data.events || [])
                                    .map(
                                        event =>
                                            `<li>${escapeHtml(event)}</li>`
                                    )
                                    .join("")
                            }
                        </ul>
                    </div>
                </div>
            </div>
        `;

    } catch (error) {
        console.error(error);

        result.innerHTML = `
            <div class="result-error">
                <span>⚠️</span>
                <p>
                    AI 추천을 가져오는 중 문제가 발생했습니다.<br>
                    잠시 후 다시 시도해주세요.
                </p>
            </div>
        `;
    } finally {
        button.disabled = false;
        button.textContent = "✨ AI에게 여행 추천받기";
    }
});


// HTML에 직접 입력되는 내용을 안전하게 처리
function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}