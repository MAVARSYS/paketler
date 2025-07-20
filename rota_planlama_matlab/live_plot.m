function live_plot(block)

    setup(block);

end

function setup(block)

    block.NumInputPorts  = 2;  % lat ve lon
    block.NumOutputPorts = 0;

    block.SetPreCompInpPortInfoToDynamic;

    for i = 1:2
        block.InputPort(i).Dimensions = 1;
        block.InputPort(i).DatatypeID = 0; % double
        block.InputPort(i).Complexity = 'Real';
        block.InputPort(i).DirectFeedthrough = true;
    end

    block.SampleTimes = [0 0];  % inherited sample time
    block.SimStateCompliance = 'DefaultSimState';

    block.RegBlockMethod('InitializeConditions', @init);
    block.RegBlockMethod('Update', @update);
end

function init(block)
    persistent h;

    figure(101); clf;
    hold on;
    h = plot(nan, nan, 'r-', 'LineWidth', 2);
    xlabel('Longitude');
    ylabel('Latitude');
    title('Canlý GPS Takibi');
    grid on;
    xlim([28.999 29.001]);
    ylim([39.999 40.001]);

    setappdata(0, 'live_plot_handle', h); % h objesini global eriþilebilir yap
end

function update(block)
    lat = block.InputPort(1).Data;
    lon = block.InputPort(2).Data;

    h = getappdata(0, 'live_plot_handle'); % grafik nesnesini al

    if isempty(h) || ~isvalid(h)
        return;
    end

    X = get(h, 'XData');
    Y = get(h, 'YData');

    set(h, 'XData', [X lon], 'YData', [Y lat]);
    drawnow limitrate;
end
