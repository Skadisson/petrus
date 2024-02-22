if __name__ == '__main__':
    from bin.service import Analyze
    from datetime import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    analyze = Analyze.Analyze()
    tickets_per_board = analyze.get_tickets_per_board(['SERVICE', 'BRANDBOXSUPPORT'])
    trend_per_board = analyze.get_trend_per_board(tickets_per_board)
    now = datetime.now()
    date = datetime.strftime(now, "%Y/%m/%d")
    figure_number = 1
    for board in tickets_per_board:
        plot_path = f'temp\\total_created_plot_{board}.png'
        x_axis = 'Datum'
        y_axis = 'Tickets'
        x_values = []
        y_values = []
        x_labels = []
        i = 1
        for month in tickets_per_board[board]:
            y_values.append(tickets_per_board[board][month])
            x_values.append(i)
            if i == 1 or str(month)[4:6] == '01':
                x_labels.append(str(month)[0:4])
            else:
                x_labels.append(None)
            i += 1
        plt.figure(figure_number)
        plt.title("Erstellte Tickets in Bord {} - Stand {}".format(board, date))
        z = np.polyfit(np.array(x_values), np.array(y_values), 2)
        p = np.poly1d(z)
        plt.xticks(x_values, x_labels)
        plt.bar(x_values, y_values, color=(['#16BAE7'] * len(y_values)))
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.grid(True)
        plt.plot(x_values, p(x_values))
        plt.savefig(plot_path)
        figure_number += 1
    print('success')
