// js/main.js

// 현재 테마를 localStorage에서 가져오거나 기본값(예: 라이트 모드) 설정
function getCurrentTheme() {
    let theme = window.localStorage.getItem('theme');
    // OS 다크모드 선호 감지 (선택적)
    if (theme === null && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        theme = 'dark'; // OS가 다크모드면 기본을 다크로
    }
    return theme || 'light'; // 저장된 값 없으면 기본 'light'
}

// 테마를 적용하는 함수
function applyTheme(theme) {
    const themeBtn = document.querySelector('.theme-toggle');
    if (theme === 'dark') {
        document.body.classList.remove('light'); // 'light' 클래스 제거
        document.body.classList.add('dark-mode');   // 'dark-mode' 클래스 추가 (CSS에 정의 필요)
        if (themeBtn) themeBtn.textContent = '☀️'; // 아이콘 변경 (밝은 모드로 전환)
    } else {
        document.body.classList.remove('dark-mode'); // 'dark-mode' 클래스 제거
        document.body.classList.add('light');      // 'light' 클래스 추가 (기존 방식 유지 또는 CSS에 정의 필요)
        if (themeBtn) themeBtn.textContent = '🌙'; // 아이콘 변경 (어두운 모드로 전환)
    }
    window.localStorage.setItem('theme', theme); // 변경된 테마를 localStorage에 저장
}

// 테마를 토글하는 함수 (기존 함수 수정)
function toggleTheme() {
    let currentTheme = getCurrentTheme();
    let newTheme = (currentTheme === 'dark') ? 'light' : 'dark';
    applyTheme(newTheme);
}

// 페이지 로드 시 저장된 테마 적용 및 버튼 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = getCurrentTheme();
    applyTheme(savedTheme);

    // 테마 토글 버튼이 여러 개 있을 수 있으므로 querySelectorAll 사용 후 각 버튼에 이벤트 리스너 추가
    const themeToggleButtons = document.querySelectorAll('.theme-toggle');
    themeToggleButtons.forEach(button => {
        button.addEventListener('click', toggleTheme);
    });

    // --- index.html에서 옮겨온 검색 관련 로직 및 기타 페이지별 로직은 여기에 두지 않거나,
    //     조건부로 실행되도록 구성해야 합니다. main.js는 공통 로직 위주로 관리하는 것이 좋습니다. ---

    // 예시: index.html 에만 해당하는 검색 로직은 index.html 내 <script> 태그로 옮기거나,
    //       아래와 같이 특정 요소 존재 여부로 실행을 제어할 수 있습니다.
    const searchInputElement_main = document.getElementById('searchInput'); // index.html의 검색창 ID
    if (searchInputElement_main) { // index.html 에만 searchInput이 있다고 가정
        // index.html의 검색 버튼 (onclick에서 직접 호출하므로 여기서는 필요 없음)
        // const searchButton_main = document.querySelector('.search-box button');
        // if (searchButton_main) {
        //     searchButton_main.addEventListener('click', performSearchFromMain); // 함수명 변경
        // }

        searchInputElement_main.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                // index.html의 performSearch 함수를 직접 호출하거나,
                // 여기서 performSearchFromMain 함수를 호출하도록 할 수 있습니다.
                // 현재 index.html 에서는 onclick="performSearch()"로 직접 호출 중이므로,
                // 이 부분은 중복될 수 있어 주의가 필요합니다.
                // 만약 onclick을 제거하고 여기서 이벤트를 걸려면 아래 주석 해제
                // performSearch(); 
            }
        });
    }
});

// 참고: index.html의 performSearch, quickSearch, showSourceDocuments, downloadResult 함수는
//       해당 페이지(index.html)의 <script> 태그 내에 있는 것이 현재 구조상 맞습니다.
//       main.js에는 여러 페이지에서 공통으로 사용될 함수(예: toggleTheme)만 두는 것이 좋습니다.