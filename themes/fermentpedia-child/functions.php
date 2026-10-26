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


/* ---------- 3. 프론트페이지 빈 공간 제거 + 진단 ---------- */

// 3a. Kadence 필터
add_filter('kadence_show_hero_title', function ($show) {
    if (is_front_page()) return false;
    return $show;
});

// 3b. 진단 JS — 헤더 아래 모든 요소에 빨간 테두리 + 클래스명 라벨 표시
//     결과 스크린샷 보내주시면 정확한 셀렉터를 잡을 수 있습니다.
//     (확인 후 이 코드는 제거됩니다)
add_action('wp_footer', function () {
    if (!is_front_page()) return;
    ?>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var header = document.querySelector('header.site-header');
        if (!header) return;
        var parent = header.parentElement;
        if (!parent) return;
        var box = document.createElement('div');
        box.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#000;color:#0f0;font:12px monospace;padding:8px;z-index:99999;max-height:40vh;overflow:auto;';
        var info = 'PARENT: <' + parent.tagName + ' class="' + parent.className + '" id="' + parent.id + '">\n\n';
        var kids = parent.children;
        for (var i = 0; i < kids.length; i++) {
            var el = kids[i];
            var rect = el.getBoundingClientRect();
            var tag = el.tagName.toLowerCase();
            var cls = (el.className || '').toString().substring(0, 80);
            var id = el.id || '';
            info += i + ': <' + tag + ' class="' + cls + '" id="' + id + '"> h=' + Math.round(rect.height) + 'px\n';
            if (rect.height > 30) {
                el.style.outline = '3px solid red';
                el.style.outlineOffset = '-3px';
                var label = document.createElement('div');
                label.style.cssText = 'background:red;color:#fff;font:bold 11px monospace;padding:2px 6px;position:relative;z-index:9999;';
                label.textContent = i + ': ' + tag + '.' + cls.split(' ')[0] + (id ? '#' + id : '') + ' [' + Math.round(rect.height) + 'px]';
                el.insertBefore(label, el.firstChild);
            }
        }
        box.textContent = info;
        document.body.appendChild(box);
    });
    </script>
    <?php
});


/* ---------- 4. 메인페이지 랜덤 피처드 포스트 ---------- */

add_action('kadence_after_header', function () {
    if (!is_front_page()) {
        return;
    }

    $all = get_posts([
        'numberposts'  => 30,
        'post_status'  => 'publish',
        'meta_key'     => '_thumbnail_id',
        'orderby'      => 'date',
        'order'        => 'DESC',
    ]);

    if (count($all) < 2) {
        return;
    }

    shuffle($all);
    $picks = array_slice($all, 0, 2);
    ?>
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
    <?php
}, 5);


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
