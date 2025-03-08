$(document).ready(function() {
    console.log('Transaction.js loaded'); // Debug log

    let selectedBooks = new Map();

    // Initialize Select2
    $('#book-select').select2({
        placeholder: 'Search for a book...',
        allowClear: true,
        minimumInputLength: 0,  // Allow showing all books without search
        ajax: {
            url: '/api/distributor-books/',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                console.log('Search params:', params); // Debug log
                return {
                    term: params.term || ''
                };
            },
            processResults: function(data) {
                console.log('Received data:', data); // Debug log
                return data;
            },
            error: function(xhr, status, error) {
                console.error('Ajax error:', error); // Debug log
            },
            cache: true
        }
    });

    // Handle book selection
    $('#book-select').on('select2:select', function(e) {
        const book = e.params.data;
        if (!selectedBooks.has(book.id)) {
            addBookToTable(book);
            selectedBooks.set(book.id, book);
        }
        $(this).val(null).trigger('change');
    });

    function addBookToTable(book) {
        const row = `
            <tr data-book-id="${book.id}">
                <td>${book.text}</td>
                <td>${book.stock}</td>
                <td>
                    <input type="number" class="form-control quantity-input" 
                           min="1" max="${book.stock}" value="1">
                </td>
                <td>${book.price}</td>
                <td class="subtotal">${book.price}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-danger remove-book">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            </tr>
        `;
        $('#selected-books tbody').append(row);
        updateTotal();
    }

    // Handle quantity changes
    $(document).on('input', '.quantity-input', function() {
        const row = $(this).closest('tr');
        const bookId = row.data('book-id');
        const book = selectedBooks.get(bookId);
        let value = parseInt($(this).val()) || 0;
        
        // Cap at maximum stock
        if (value > book.stock) {
            value = book.stock;
            $(this).val(value);
        }
        
        const subtotal = value * book.price;
        row.find('.subtotal').text(subtotal.toFixed(2));
        updateTotal();
    });

    // Handle book removal
    $(document).on('click', '.remove-book', function() {
        const row = $(this).closest('tr');
        const bookId = row.data('book-id');
        selectedBooks.delete(bookId);
        row.remove();
        updateTotal();
    });

    function updateTotal() {
        let total = 0;
        $('.subtotal').each(function() {
            total += parseFloat($(this).text());
        });
        $('#total-amount').text(total.toFixed(2));
    }

    // Handle form submission
    $('#transaction-form').on('submit', function(e) {
        e.preventDefault();
        
        const booksData = [];
        $('#selected-books tbody tr').each(function() {
            const bookId = $(this).data('book-id');
            const quantity = $(this).find('.quantity-input').val();
            booksData.push({
                dist_book_id: bookId,
                quantity: quantity
            });
        });

        const formData = new FormData(this);
        formData.append('books', JSON.stringify(booksData));
        formData.append('total_amount', $('#total-amount').text());

        $.ajax({
            url: $(this).attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    // Format and display the error message
                    let errorMessage = '';
                    if (typeof response.error === 'object') {
                        // Handle form field errors
                        Object.keys(response.error).forEach(key => {
                            errorMessage += `${key}: ${response.error[key]}\n`;
                        });
                    } else {
                        // Handle string error messages
                        errorMessage = response.error;
                    }
                    alert(errorMessage || 'An error occurred while processing your request.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Ajax error:', error);
                alert('An error occurred while processing your request. Please try again.');
            }
        });
    });
});