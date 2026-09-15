.pragma library
.import "IndicatorStyles.js" as IndicatorStyles

function computeGeometry(a) {
    const w = _width(a);
    const h = _height(a);

    const x = _x(Object.assign({}, a, { widthValue: w }));
    const y = _y(Object.assign({}, a, { heightValue: h }));

    const r = _radius(a);

    return { w, h, x, y, r };
}

function _width(args) {
    const {
        style, config,
        isVertical, parentWidth,
        labelImplicitWidth,
        spacing,
        fillButton,
        usesLabelMetrics
    } = args;

    if (config.LabelStyle === 5) {
        return style === IndicatorStyles.SideLine
            ? config.IndicatorLineThickness : config.NoneIndicatorWidth;
    }

    if (isVertical) {
        if (style === IndicatorStyles.SideLine)
            return config.IndicatorLineThickness;

        if (fillButton)
            return parentWidth + 0.5 - 2 * spacing;

        if (usesLabelMetrics)
            return labelImplicitWidth + 2 * config.ButtonMarginHorizontal;

        return parentWidth + 0.5 - 2 * spacing;
    }

    if (style === IndicatorStyles.SideLine)
        return config.IndicatorLineThickness;

    return parentWidth + 0.5 - 2 * spacing;
}

function _height(args) {
    const {
        style, config,
        isVertical, parentHeight,
        labelImplicitHeight,
        usesLabelMetrics
    } = args;

    if (config.LabelStyle === 5) {
        return style === IndicatorStyles.EdgeLine
            ? config.IndicatorLineThickness : config.NoneIndicatorHeight;
    }

    if (style === IndicatorStyles.FullSize) {
        if (isVertical)
            return parentHeight + 0.5 - 2 * config.ButtonSpacing;

        return parentHeight;
    }

    if (usesLabelMetrics)
        return labelImplicitHeight + 2 * config.ButtonMarginVertical;

    return config.IndicatorLineThickness;
}

function _x(args) {
    const {
        style, config,
        isVertical, parentWidth,
        widthValue,
        spacing,
        fillButton
    } = args;

    if (config.LabelStyle === 5) {
        if (style === IndicatorStyles.SideLine) {
            const inset = (parentWidth - config.NoneIndicatorWidth) / 2;
            return config.IndicatorInvert ? parentWidth - widthValue - inset : inset;
        }
        return (parentWidth - widthValue) / 2;
    }

    if (isVertical) {
        if (style !== IndicatorStyles.SideLine)
            return fillButton ? spacing : (parentWidth - widthValue) / 2;

        return config.IndicatorInvert
            ? parentWidth - config.IndicatorLineThickness
            : 0;
    }

    if (style === IndicatorStyles.SideLine && config.IndicatorInvert)
        return parentWidth - widthValue - spacing;

    return spacing;
}

function _y(args) {
    const {
        style, config,
        parentHeight,
        heightValue,
        isTopLocation,
        usesLabelMetrics
    } = args;

    if (usesLabelMetrics || (config.LabelStyle === 5 && style !== IndicatorStyles.EdgeLine))
        return (parentHeight - heightValue) / 2;

    if (isTopLocation)
        return !config.IndicatorInvert
            ? parentHeight - heightValue
            : 0;

    return !config.IndicatorInvert
        ? 0
        : parentHeight - heightValue;
}

function _radius(args) {
    const { style, config } = args;

    if (config.LabelStyle === 5 &&
        (style === IndicatorStyles.Block || style === IndicatorStyles.Rounded)) {
        return Math.min(config.NoneIndicatorRadius, config.NoneIndicatorWidth / 2, config.NoneIndicatorHeight / 2);
    }

    if (style === IndicatorStyles.Block)
        return config.IndicatorBlockRadius;

    if (style === IndicatorStyles.Rounded)
        return 300;

    return 0;
}
