document.addEventListener("DOMContentLoaded", function () {
  // 現在の年を設定
  document.getElementById("current-year").textContent =
    new Date().getFullYear();

  // サイドバーのアクティブリンク設定
  setupSidebar();

  // マークダウンコンテンツの読み込み
  loadMarkdownContents();
});

function setupSidebar() {
  // スクロール時にアクティブなセクションを更新
  window.addEventListener("scroll", updateActiveSection);

  // サイドバーリンクのクリックイベント
  const sidebarLinks = document.querySelectorAll(".sidebar a");
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const targetId = this.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 40,
          behavior: "smooth",
        });
      }
    });
  });
}

function updateActiveSection() {
  const sections = document.querySelectorAll("section");
  const scrollPosition = window.scrollY + 100;

  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.offsetHeight;
    const sectionId = section.getAttribute("id");

    if (
      scrollPosition >= sectionTop &&
      scrollPosition < sectionTop + sectionHeight
    ) {
      // 現在のアクティブリンクを削除
      document.querySelectorAll(".sidebar a").forEach((link) => {
        link.classList.remove("active");
      });

      // 新しいアクティブリンクを設定
      const activeLink = document.querySelector(
        `.sidebar a[href="#${sectionId}"]`
      );
      if (activeLink) {
        activeLink.classList.add("active");
      }
    }
  });
}

async function loadMarkdownContents() {
  try {
    console.log("Loading markdown contents...");

    // メタデータの読み込み
    const metadataResponse = await fetch("_auto_contents/metadata.yml");
    console.log("Metadata response:", metadataResponse);
    if (metadataResponse.ok) {
      const metadata = await metadataResponse.text();

      // YAMLパース（簡易実装）
      const lastUpdatedMatch = metadata.match(/last_updated:\s*(.*)/);
      if (lastUpdatedMatch && lastUpdatedMatch[1]) {
        document.getElementById("last-updated").textContent =
          lastUpdatedMatch[1].trim();
      }
    }

    // 各コンテンツセクションを読み込む
    const contentElements = document.querySelectorAll(
      ".markdown-content[data-source]"
    );

    for (const element of contentElements) {
      const sourcePath = element.getAttribute("data-source");
      await loadMarkdownFromSource(element, sourcePath);
    }
  } catch (error) {
    console.error("コンテンツ読み込みエラー:", error);
    document.querySelectorAll(".loading").forEach((el) => {
      el.textContent = "データの読み込みに失敗しました。";
    });
  }
}

async function loadMarkdownFromSource(element, sourcePath) {
  try {
    // パスの先頭にスラッシュを追加して絶対パスに変換
    const absolutePath = sourcePath.startsWith("/")
      ? sourcePath
      : `/${sourcePath}`;
    const response = await fetch(absolutePath);
    if (!response.ok) {
      // ファイルが存在しない場合はセクションを非表示にする
      const sectionElement = element.closest("section");
      if (sectionElement) {
        sectionElement.style.display = "none";

        // サイドバーのリンクも非表示にする
        const sectionId = sectionElement.id;
        const sidebarLink = document.querySelector(
          `.sidebar a[href="#${sectionId}"]`
        );
        if (sidebarLink) {
          sidebarLink.parentElement.style.display = "none";
        }
      }
      return;
    }

    const markdownText = await response.text();

    // マークダウンが空の場合もセクションを非表示にする
    if (!markdownText.trim() || markdownText.trim() === "") {
      const sectionElement = element.closest("section");
      if (sectionElement) {
        sectionElement.style.display = "none";

        // サイドバーのリンクも非表示にする
        const sectionId = sectionElement.id;
        const sidebarLink = document.querySelector(
          `.sidebar a[href="#${sectionId}"]`
        );
        if (sidebarLink) {
          sidebarLink.parentElement.style.display = "none";
        }
      }
      return;
    }

    // Front Matter（YAML）を削除
    const content = removeFrontMatter(markdownText);

    // マークダウンをHTMLに変換
    element.innerHTML = marked.parse(content);

    // プロフィール写真の挿入（プロフィールセクションの場合のみ）
    if (element.id === "profile-content") {
      insertProfileImage();
    }
  } catch (error) {
    console.error(`${absolutePath}読み込みエラー:`, error);
    // エラーの場合もセクションを非表示にする
    const sectionElement = element.closest("section");
    if (sectionElement) {
      sectionElement.style.display = "none";

      // サイドバーのリンクも非表示にする
      const sectionId = sectionElement.id;
      const sidebarLink = document.querySelector(
        `.sidebar a[href="#${sectionId}"]`
      );
      if (sidebarLink) {
        sidebarLink.parentElement.style.display = "none";
      }
    }
  }
}

function removeFrontMatter(markdown) {
  // Front Matter（---で囲まれた部分）を削除する
  return markdown.replace(/^---[\s\S]*?---\n/, "");
}

// Markdownコンテンツの読み込みと変換
function loadMarkdownContent() {
  document.querySelectorAll(".markdown-content").forEach((element) => {
    const sourceFile = element.getAttribute("data-source");
    fetch(sourceFile)
      .then((response) => response.text())
      .then((text) => {
        // タイトル行を除外する処理（オプション）
        const contentWithoutTitle = text.replace(/^# .*$/m, "");
        element.innerHTML = marked.parse(contentWithoutTitle);
      })
      .catch((error) => {
        console.error("Markdown loading error:", error);
        element.innerHTML = "<p>コンテンツの読み込みに失敗しました。</p>";
      });
  });
}

// プロフィール写真を挿入する関数
function insertProfileImage() {
  const profileContent = document.getElementById("profile-content");
  const firstHeading = profileContent.querySelector("h2"); // CareerまたはEducationの見出し

  if (firstHeading) {
    const imageHTML = `
      <div class="profile-with-image">
        <div class="profile-info">
          ${profileContent.innerHTML.slice(
            0,
            profileContent.innerHTML.indexOf("<h2")
          )}
        </div>
        <div class="profile-image">
          <img src="assets/images/profile.jpg" alt="Kenji Kubo" />
        </div>
        <div class="clear"></div>
      </div>
      ${profileContent.innerHTML.slice(profileContent.innerHTML.indexOf("<h2"))}
    `;
    profileContent.innerHTML = imageHTML;
  }
}
