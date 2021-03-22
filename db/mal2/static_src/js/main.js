/* global
autosize
bsCustomFileInput
checkRedirect
initHtmlTextarea
updateHtmlContent
*/


// #############################################################################
// GLOBAL VARS

const $body = $("body");


// #############################################################################
// FOCUS

$body.betterFocus({
  selector: "a, [tabindex]",
});


// #############################################################################
// TOOLTIP

$("[data-toggle=tooltip]").tooltip();


// #############################################################################
// FORM

function initFormDefaults ($parent = $body) {
  // File
  bsCustomFileInput.init();

  // Autosize
  autosize($("textarea", $parent));

  // HTML TinyMCE
  initHtmlTextarea($parent);

  // Range
  $("[type=range]", $parent).formRange();

  // Ajax upload
  $("[data-ajax-upload]", $parent).ajaxUpload({
    onUploadCompleted: function ($upload, $data) {
      updateHtmlContent($data);
    },
  });

  // Wizard
  $("[data-form=\"wizard\"]", $parent).formWizard();

  // File tree
  $("[data-file-tree]", $parent).formFileTree();

  // Form set

  $("[data-form-set]", $parent).formSet();
}

initFormDefaults();

// Validation

$("[data-form]").formValidation({
  afterSubmit: function (request, $form, $data) {
    if ($data.submit === "success") {
      checkRedirect($data);
      updateHtmlContent($data);

      if ($data.toaster) {
        $body.toaster("updateToaster", $data.toaster);
      }
    }
  },
});

// Wizard

$("[data-form-wizard]").formWizard();


// #############################################################################
// AJAX MODAL

$body.ajaxModal({
  selector: "[data-modal-link]",
  beforeModalOpen: function ($modal, $data) {
    if ($data.submit === "error") {
      if ($data.toaster) {
        $body.toaster("updateToaster", $data.toaster);
      }
    }
  },
  onModalOpen: function ($modal) {
    $("[autofocus]", $modal).focus();
    $("[data-toggle=tooltip]", $modal).tooltip();

    initFormDefaults($modal);

    // Validation

    $("[data-form]", $modal).formValidation({
      afterSubmit: function (request, $form, $data) {
        if ($data.submit === "success") {
          $modal.modal("hide");

          checkRedirect($data);
          updateHtmlContent($data);

          if ($data.toaster) {
            $body.toaster("updateToaster", $data.toaster);
          }

          $("[data-table]").xDataTable("reload");
        }
      },
    });

    // Wizard

    $("[data-form-wizard]", $modal).formWizard();
  },
});


// #############################################################################
// DATA TABLE

$("[data-table]").xDataTable({
  options: {
    columns: [
      {
        data: "PLACEHOLDER_FIELDS",
      },
    ],
  },
  onInit: function ($table, $json) {
    // Custom code on init
  },
  onStateLoaded: function ($table, $data) {
    // Custom code on init
  },
  onDraw: function ($table) {
    // Custom code on redraw

    $("[data-toggle=tooltip]", $table).tooltip();
  },
  customizeCSV: function (csv) {
    // For customization read https://datatables.net/reference/button/csv

    return csv;
  },
});


// #############################################################################
// DOWNLOAD BLOB

$("[data-download]").downloadBlob({
  onDownloadStarted: function ($data) {
    $body.toaster("updateToaster", $data.toaster);
  },
});


// #############################################################################
// CLIPBOARD

$body.clipBoard({
  selector: "[data-clipboard]",
});


// #############################################################################
// TOASTER

$body.toaster({
  selector: "[data-toaster]",
});


// #############################################################################
// AUTO UPDATE HTML CONTENT

$body.autoUpdateHtmlContent({
  selector: "[data-update-html-content]",
});
