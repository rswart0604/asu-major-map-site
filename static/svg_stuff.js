function foo() {
    try {


        const svgImage = document.getElementById("major_map_svg");
        console.log(svgImage);
        const svgContainer = document.getElementById("svg_container");

        var viewBox = {x: -2, y: -66.8, w: 1889.68, h: 1377.76};

        const svgSize = {w: svgImage.clientWidth, h: svgImage.clientHeight};
        console.log(svgSize);
        var isPanning = false;
        var startPoint = {x: 0, y: 0};
        var endPoint = {x: 0, y: 0};

        var scale = 1;

        svgContainer.onwheel = function (e) {
            e.preventDefault();
            var w = viewBox.w;
            var h = viewBox.h;
            var mx = e.x;//mouse x
            var my = e.y;
            var dw = w * -Math.sign(e.deltaY) * 0.05;
            var dh = h * -Math.sign(e.deltaY) * 0.05;
            var dx = dw * mx / svgSize.w;
            var dy = dh * my / svgSize.h;
            viewBox = {x: viewBox.x + dx, y: viewBox.y + dy, w: viewBox.w - dw, h: viewBox.h - dh};
            scale = svgSize.w / viewBox.w;
            // zoomValue.innerText = `${Math.round(scale * 100) / 100}`;
            svgImage.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
            console.log(svgImage.clientWidth);
            if (svgImage.clientWidth == 0) {
                throw 'ah!';
            }
            console.log(svgImage);
            console.log(this);
            console.log('scale: ' + scale.toString());
            // console.log(svgImage.viewBox);
        }


        svgContainer.onmousedown = function (e) {
            isPanning = true;
            startPoint = {x: e.x, y: e.y};
        }

        svgContainer.onmousemove = function (e) {
            if (isPanning) {
                console.log('panning!');
                endPoint = {x: e.x, y: e.y};
                var dx = (startPoint.x - endPoint.x) / scale;
                var dy = (startPoint.y - endPoint.y) / scale;
                var movedViewBox = {x: viewBox.x + dx, y: viewBox.y + dy, w: viewBox.w, h: viewBox.h};
                svgImage.setAttribute('viewBox', `${movedViewBox.x} ${movedViewBox.y} ${movedViewBox.w} ${movedViewBox.h}`);
            }
            console.log('move');
        }


        svgContainer.onmouseup = function (e) {
            if (isPanning) {
                endPoint = {x: e.x, y: e.y};
                var dx = (startPoint.x - endPoint.x) / scale;
                var dy = (startPoint.y - endPoint.y) / scale;
                viewBox = {x: viewBox.x + dx, y: viewBox.y + dy, w: viewBox.w, h: viewBox.h};
                svgImage.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
                isPanning = false;
            }
        }

        svgContainer.onmouseleave = function (e) {
            isPanning = false;
        }

        function quit() {
            throw 'outta here';
        }

    } catch (err) {
        console.log('hasnt been loaded');
        console.log(err)
    }
}