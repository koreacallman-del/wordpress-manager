<?php
/**
 * Fermentpedia Child Theme — functions.php
 *
 * 1. 부모 테마 + 차일드 CSS 로드
 * 2. 고정 헤더 (sticky header) JS
 * 3. 프론트페이지 Kadence 히어로 제거
 * 4. 메인페이지 랜덤 피처드 포스트 2개
 * 5. 글 레이아웃: 이미지·제목 겹침 제거
 */

defined('ABSPATH') || exit;

/* ---------- 1. 스타일 로드 ---------- */

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'kadence-parent',
        get_template_directory_uri() . '/style.css'
    );
    wp_enqueue_style(
        'fermentpedia-child',
        get_stylesheet_uri(),
        ['kadence-parent'],
        wp_get_theme()->get('Version')
    );
});


/* ---------- 2. 고정 헤더 JS ---------- */

add_action('wp_footer', function () {
    ?>
    <script>
    (function() {
        var header = document.querySelector('header.site-header');
        if (!header) return;

        var last = 0;
        var ticking = false;

        function onScroll() {
            last = window.scrollY;
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    header.classList.toggle('is-sticky', last > 10);
                    ticking = false;
                });
                ticking = true;
            }
        }

        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    })();
    </script>
    <?php
});


/* ---------- 3. 프론트페이지 빈 공간 제거 ---------- */

add_filter('kadence_show_hero_title', function ($show) {
    if (is_front_page()) return false;
    return $show;
});

add_action('wp_head', function () {
    if (!is_front_page()) return;
    ?>
    <style>
        .home #inner-wrap {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
    </style>
    <?php
});

/* ---------- 4. 메인페이지 랜덤 피처드 포스트 ---------- */

// 4a. hidden div로 카드 HTML을 wp_footer에 출력
add_action('wp_footer', function () {
    if (!is_front_page()) return;

    $all = get_posts([
        'numberposts'  => 30,
        'post_status'  => 'publish',
        'meta_key'     => '_thumbnail_id',
        'orderby'      => 'date',
        'order'        => 'DESC',
    ]);

    if (count($all) < 2) return;

    shuffle($all);
    $picks = array_slice($all, 0, 2);
    ?>
    <div id="fp-featured-pending" style="display:none">
        <div class="fp-featured-wrap">
            <div class="fp-featured-grid">
                <?php foreach ($picks as $p) :
                    $img = get_the_post_thumbnail_url($p->ID, 'large');
                    $cat = get_the_category($p->ID);
                    $cat_name = !empty($cat) ? esc_html($cat[0]->name) : '';
                ?>
                <a href="<?php echo get_permalink($p->ID); ?>" class="fp-featured-card">
                    <div class="fp-featured-img" style="background-image:url('<?php echo esc_url($img); ?>')"></div>
                    <div class="fp-featured-info">
                        <?php if ($cat_name) : ?>
                            <span class="fp-featured-cat"><?php echo $cat_name; ?></span>
                        <?php endif; ?>
                        <h3 class="fp-featured-title"><?php echo esc_html($p->post_title); ?></h3>
                    </div>
                </a>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
    <script>
    (function() {
        var pending = document.getElementById('fp-featured-pending');
        var target = document.getElementById('inner-wrap');
        if (!pending || !target) return;
        var wrap = pending.querySelector('.fp-featured-wrap');
        if (!wrap) return;
        var firstChild = target.firstElementChild;
        if (firstChild) {
            firstChild.insertAdjacentElement('afterend', wrap);
        } else {
            target.insertBefore(wrap, target.firstChild);
        }
        pending.remove();

        var kids = target.children;
        for (var i = 1; i < kids.length; i++) {
            var el = kids[i];
            if (el.classList.contains('fp-featured-wrap')) continue;
            var rect = el.getBoundingClientRect();
            var text = (el.textContent || '').trim();
            if (rect.height > 20 && rect.height < 300 && text.length === 0 && !el.querySelector('img, video, iframe, canvas')) {
                el.style.display = 'none';
            } else {
                break;
            }
        }
    })();
    </script>
    <?php
});


/* ---------- 5. 글 레이아웃: 이미지·제목 겹침 제거 ---------- */

add_filter('theme_mod_post_title_layout', function () {
    return 'normal';
});

add_filter('theme_mod_post_title_inner_layout', function () {
    return 'standard';
});

add_filter('theme_mod_post_title_featured_placement', function () {
    return 'above';
});

add_filter('theme_mod_post_feature_position', function () {
    return 'above';
});

add_filter('theme_mod_post_title_element_feature', function ($val) {
    if (is_array($val)) {
        $val['enabled'] = true;
    }
    return $val;
});
