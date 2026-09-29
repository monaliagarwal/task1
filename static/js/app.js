// PulseFeed Client Application Script

document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Toggle Controller (Triggers BUG-07 Contrast Defect)
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const appBody = document.getElementById('app-body');

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            if (appBody.classList.contains('light-theme')) {
                appBody.classList.remove('light-theme');
                appBody.classList.add('dark-theme');
                themeIcon.classList.remove('bi-moon-stars');
                themeIcon.classList.add('bi-sun');
                localStorage.setItem('pf_theme', 'dark');
            } else {
                appBody.classList.remove('dark-theme');
                appBody.classList.add('light-theme');
                themeIcon.classList.remove('bi-sun');
                themeIcon.classList.add('bi-moon-stars');
                localStorage.setItem('pf_theme', 'light');
            }
        });
    }

    // 2. Favorite Toggle Handler
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const articleId = btn.dataset.id;
            try {
                const res = await fetch(`/api/articles/${articleId}/favorite/`, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                if (res.status === 401) {
                    window.location.href = '/login/';
                    return;
                }
                const data = await res.json();
                const icon = btn.querySelector('i');
                const countSpan = btn.querySelector('.fav-count');
                
                countSpan.textContent = data.favorites_count;
                if (data.favorited) {
                    btn.classList.remove('btn-outline-primary');
                    btn.classList.add('btn-primary');
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                } else {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary');
                    icon.classList.remove('bi-heart-fill');
                    icon.classList.add('bi-heart');
                }
            } catch (err) {
                console.error('Error toggling favorite:', err);
            }
        });
    });

    // 3. Comment Submission Handler
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const articleId = commentForm.dataset.articleId;
            const bodyInput = document.getElementById('comment-body');
            const commentText = bodyInput.value.trim();

            if (!commentText) return;

            try {
                const res = await fetch(`/api/articles/${articleId}/comments/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ body: commentText })
                });

                if (res.ok) {
                    const data = await res.json();
                    bodyInput.value = '';
                    const commentsContainer = document.getElementById('comments-container');
                    const noCommentsMsg = document.getElementById('no-comments-msg');
                    if (noCommentsMsg) noCommentsMsg.remove();

                    const newCommentCard = document.createElement('div');
                    newCommentCard.className = 'card mb-3 border-0 bg-light rounded-3 shadow-sm';
                    newCommentCard.innerHTML = `
                        <div class="card-body p-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="fw-bold text-dark"><i class="bi bi-person-circle me-1 text-secondary"></i> ${data.comment.author}</span>
                                <small class="text-muted">${data.comment.created_at}</small>
                            </div>
                            <p class="card-text mb-0">${data.comment.body}</p>
                        </div>
                    `;
                    commentsContainer.prepend(newCommentCard);
                } else {
                    alert('Failed to post comment. Check server response.');
                }
            } catch (err) {
                console.error('Comment submission error:', err);
            }
        });
    }

    // 4. Delete Article Button Handler (BUG-01: IDOR endpoint call)
    const deleteBtn = document.getElementById('delete-article-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async (e) => {
            const articleId = deleteBtn.dataset.id;
            if (!confirm(`Are you sure you want to delete Article #${articleId}?`)) return;

            try {
                const res = await fetch(`/api/articles/${articleId}/delete/`, {
                    method: 'POST'
                });
                const data = await res.json();
                if (res.ok) {
                    alert('Article deleted: ' + data.message);
                    window.location.href = '/';
                } else {
                    alert('Delete failed: ' + (data.error || 'Server error'));
                }
            } catch (err) {
                console.error('Delete request error:', err);
            }
        });
    }
});
