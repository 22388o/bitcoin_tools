from bitcoin_tools.analysis.plots import get_cdf
from data_processing import get_samples
from bitcoin_tools.analysis.status.plots import plots_from_samples
from bitcoin_tools import CFG
from ujson import load
from getopt import getopt
from sys import argv


def compare_dust(dust_files, legend, version):
    """
    Compares dust of two given dust files.

    :param dust_files: List of dust file names
    :type dust_files: list of str
    :param legend: Legend for the charts
    :type legend: list of str
    :param version: Bitcoin core version, used to decide the folder in which to store the data.
    :type version: float
    :return: None
    :rtype: None
    """

    outs = ["cmp_dust_utxos", "cmp_dust_value", "cmp_dust_data_len"]
    totals = ['total_utxos', 'total_value', 'total_data_len']

    utxos = []
    value = []
    length = []

    for f in dust_files:
        data = load(open(CFG.data_path + f))
        utxos.append(data['np_utxos'])
        value.append(data['np_value'])
        length.append(data['np_data_len'])

    xs_utxos, ys_utxos = [sorted(u.keys(), key=int) for u in utxos], [sorted(u.values(), key=int) for u in utxos]
    xs_value, ys_value = [sorted(v.keys(), key=int) for v in value], [sorted(v.values(), key=int) for v in value]
    xs_length, ys_length = [sorted(l.keys(), key=int) for l in length], [sorted(l.values(), key=int) for l in length]

    x_samples = [xs_utxos, xs_value, xs_length]
    y_samples = [ys_utxos, ys_value, ys_length]

    for xs, ys, out, total in zip(x_samples, y_samples, outs, totals):
        plots_from_samples(xs=xs, ys=ys, save_fig=out, legend=legend, xlabel='Fee rate(sat/byte)',
                           ylabel="Number of UTXOs", version=str(version))

        # Get values in percentage
        ys_perc = []
        for y_samples in ys:
            y_perc = [y / float(data[total]) for y in y_samples]
            ys_perc.append(y_perc)

        plots_from_samples(xs=xs, ys=ys_perc, save_fig='perc_' + out, legend=legend,
                           xlabel='Fee rate(sat/byte)', ylabel="Number of UTXOs", version=str(version))


def compare_attribute(fin_names, x_attribute, xlabel='', legend='', out_name, version):
    """
    Performs a comparative analysis between different files and a fixed attribute. Useful to compare the evolution
    of a parameter throughout different snapshots.

    :param fin_names: List of file names to load data from.
    :type fin_names: list str
    :param x_attribute: Attribute to be compared.
    :type x_attribute: str
    :param xlabel: Label of the x axis of the resulting chart.
    :type xlabel: str
    :param legend: Legend to be included in the chart.
    :type legend: str
    :param out_name: Name of the generated chart.
    :type out_name: str
    :param version: Bitcoin core version, used to decide the folder in which to store the data.
    :type version: float
    :return: None
    :rtyp: None
    """

    samples = [get_samples(x_attribute, fin) for fin in fin_names]

    xs = []
    ys = []
    for _ in range(len(samples)):
        x, y = get_cdf(samples.pop(0).values(), normalize=True)
        xs.append(x)
        ys.append(y)

    plots_from_samples(xs=xs, ys=ys, xlabel=xlabel, save_fig=out_name, version=str(version), legend=legend,
                       log_axis='x', ylabel="Number of UTXOs", legend_loc=2)


def comparative_data_analysis(tx_fin_name, utxo_fin_name, version):
    """
    Performs a comparative data analysis between a transaction dump data file and an utxo dump one.

    :param tx_fin_name: Input file path which contains the chainstate transaction dump.
    :type: str
    :param utxo_fin_name: Input file path which contains the chainstate utxo dump.
    :type: str
    :param version: Bitcoin core version, used to decide the folder in which to store the data.
    :type version: float
    :return: None
    :rtype: None
    """

    # Generate plots with both transaction and utxo data (f_parsed_txs and f_parsed_utxos)
    tx_attributes = ['total_value', 'height']
    utxo_attributes = ['amount', 'tx_height']

    xlabels = ['Amount (Satoshi)', 'Height']
    out_names = ['tx_utxo_amount', 'tx_utxo_height']
    legends = [['Tx.', 'UTXO'], ['Tx.', 'UTXO']]
    legend_locations = [1, 2]

    tx_samples = get_samples(tx_attributes, tx_fin_name)
    utxo_samples = get_samples(utxo_attributes, utxo_fin_name)

    for tx_attr, utxo_attr, label, out, legend, leg_loc in zip(tx_attributes, utxo_attributes, xlabels, out_names,
                                                               legends, legend_locations):
        xs_txs, ys_txs = get_cdf(tx_samples[tx_attr], normalize=True)
        xs_utxos, ys_utxos = get_cdf(utxo_samples[utxo_attr], normalize=True)

        plots_from_samples(xs=[xs_txs, xs_utxos], ys=[ys_txs, ys_utxos], xlabel=label, save_fig=out,
                           version=str(version), legend=legend, legend_loc=leg_loc, ylabel="Number of registers")


def run_experiment(version, f_dust, f_parsed_utxos, f_parsed_txs):
    """
    Runs the whole experiment. You may comment the parts of it you are not interested in to save time.

     :param version: Bitcoin core version, used to decide the folder in which to store the data.
    :type version: float
    :return:
    """

    print "Running comparative data analysis."
    # Comparative dust analysis between different snapshots

    print "Comparing dust from different snapshots."
    # Get dust files from different dates to compare (Change / Add the ones you'll need)
    dust_files = [str(version) + '/height-' + str(i) + 'K/' + f_dust + '.json' for i in range(100, 550, 50)]
    legend = [str(i) + 'K' for i in range(100, 550, 50)]
    compare_dust(dust_files=dust_files, legend=legend, version=version)

    # Comparative analysis between different snapshots
    # Get parsed_utxos files from different dates to compare (Change / Add the ones you'll need)
    fin_names = [str(version) + '/height-' + str(i) + 'K/' + f_parsed_utxos + '.json' for i in range(100, 550, 50)]
    legend = [str(i) + 'K' for i in range(100, 550, 50)]

    # UTXO amount comparison
    print "Comparing UTXO amount from different snapshots."
    compare_attribute(fin_names=fin_names, x_attribute='amount', xlabel='Amount (Satoshi)', legend=legend,
                      out_name='cmp_utxo_amount', version=version)

    # UTXO size comparison
    print "Comparing UTXO size from different snapshots."
    compare_attribute(fin_names=fin_names, x_attribute='register_len', xlabel='Size (bytes)', legend=legend,
                      out_name='cmp_utxo_size', version=version)

    # Comparative data analysis (transactions and UTXOs)
    comparative_data_analysis(f_parsed_txs, f_parsed_utxos, version)


if __name__ == '__main__':

    f_dust = 'dust_wp2sh'
    f_parsed_utxos = 'parsed_utxos_wp2sh'
    f_parsed_txs = 'parsed_txs'

    # Set version and chainstate dir name
    version = 0.15

    run_experiment(version, f_dust, f_parsed_utxos, f_parsed_txs)