document.addEventListener("DOMContentLoaded", function () {
  // プロフィールコンテンツを読み込む
  fetch("_auto_contents/profile.md")
    .then((response) => {
      console.log("Profile fetch response:", response);
      if (!response.ok) throw new Error("Failed to load profile");
      return response.text();
    })
    .then((markdown) => {
      console.log("Markdown loaded:", markdown.substring(0, 100) + "...");
      document.getElementById("profile-content").innerHTML =
        marked.parse(markdown);
    })
    .catch((error) => {
      console.error("Error loading profile:", error);
      document.getElementById("profile-content").innerHTML =
        "<p>Error loading content. Please try again later.</p>";
    });
});
