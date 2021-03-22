/* global
 bsCustomFileInput
 gettext
 tinymce
 */


// #############################################################################
// GLOBAL VARS

const $window = $(window);
const $html = $("html");
const $body = $("body");


// #############################################################################
// AJAX SETUP

function csrfSafeMethod (method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  cache: false,
  beforeSend: function ($xhr, $settings) {
    if (!csrfSafeMethod($settings.type) && !this.crossDomain) {
      $xhr.setRequestHeader(
        "X-CSRFToken", $("[name=csrfmiddlewaretoken]").val()
      );
    }
  },
  error: function (e) {
    console.log("ERROR:", e, e.status, e.statusText);
  },
});


// #############################################################################
// JQUERY PLUGIN HELPER

function initPlugin (Plugin, plugin_name) {
  return function ($options) {
    const $args = Array.prototype.slice.call(arguments, 1);

    if ($options === undefined || typeof $options === "object") {
      return this.each(function () {
        if (!$.data(this, "plugin_" + plugin_name)) {
          $.data(this, "plugin_" + plugin_name, new Plugin(this, $options));
        }
      });
    } else if (typeof $options === "string") {
      this.each(function () {
        const $instance = $.data(this, "plugin_" + plugin_name);

        if ($instance && typeof $instance[$options] === "function") {
          $instance[$options].apply($instance, $args);
        } else {
          throw new Error("Method " + $options + " does not exist on jQuery." + plugin_name);
        }
      });
    }
  };
}


// #############################################################################
// HELPERS

/**
 * formatFileSize() outputs human readable file size.
 *
 * Args:
 *  bytes (int): Bytes
 *  decimal_point (int): Decimal point
 *
 * Returns:
 *  str: A human readable string with unit.
 *
 **/

function formatFileSize (bytes, decimal_point) {
  if (bytes === 0) {
    return "0 Bytes";
  }

  const k = 1000;
  const dm = decimal_point || 2;
  const sizes = ["Bytes", "kb", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

/**
 * updateHtmlContent() updates multiple HTML content from ajax response.
 *
 * Args:
 *  $data (obj): JSON object
 *
 * Example:
 *  $data = {
 *    "updates": [
 *      {
 *        "wrapper": "#id_to_insert_content",
 *        "content": "<p>Updated content</p>",
 *      },
 *    ],
 *  }
 *
 **/

function updateHtmlContent ($data, $parent = $body) {
  if ($data.updates) {
    $data.updates.forEach(function ($item) {
      $($item.wrapper, $parent).html($item.content);
    });
  }
}

/**
 * escapeText() remove HTML tags from string.
 *
 **/

function escapeText (text) {
  const tags_to_replace = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
  };

  return text.replace(/[&<>]/g, function (tag) {
    return tags_to_replace[tag] || tag;
  });
}


// #############################################################################
// REDIRECT

function checkRedirect ($data) {
  if ($data.redirect) {
    if ($data.toaster) {
      $body.toaster("saveToaster", $data.toaster);
    }

    window.location.href = $data.redirect;
  }
}


// #############################################################################
// FOCUS

/**
 * Initial:
 *
 * $("body").betterFocus({
 *  selector: "a, [tabindex]",
 * });
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "betterFocus";

  const $defaults = {
    selector: "a, [tabindex]",
  };

  class betterFocusPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.el = $element;
      this.$el = $($element);

      this.focus_method = false;
      this.last_focus_method = false;

      this.init();
    }

    init () {
      const _this = this;

      this.$el.on("focus", _this.$settings.selector, function () {
        if (!_this.focus_method) {
          _this.focus_method = _this.last_focus_method;
        }

        $(_this.$settings.selector).attr("data-focus-method", _this.focus_method);

        _this.last_focus_method = _this.focus_method;
        _this.focus_method = false;
      });

      $body.on("blur", _this.$settings.selector, function () {
        $(_this.$settings.selector).removeAttr("data-focus-method");
      });

      $window.on("blur", function () {
        _this.focus_method = false;
      });

      // Keyboard

      $body.on("keydown", _this.$settings.selector, function () {
        _this.focus_method = "key";
      });

      // Mouse

      $body.on("mousedown", _this.$settings.selector, function () {
        if (_this.focus_method === "touch") {
          return;
        }

        _this.focus_method = "mouse";
      });

      // Touch

      $body.on("touchstart", _this.$settings.selector, function () {
        _this.focus_method = "touch";
      });
    }
  }

  $.fn[plugin_name] = initPlugin(betterFocusPlugin, plugin_name);
})(jQuery);


// #############################################################################
// FORM: RANGE

(function ($) {
  "use strict";

  const plugin_name = "formRange";

  class formRangePlugin {
    constructor ($element) {
      this.$el = $($element);

      this.$label = $("label[for=" + this.$el.attr("id") + "]");
      this.$value = $("[data-range-value]", this.$label);

      this.init();
    }

    init () {
      const _this = this;

      _this.$el.on("input", function () {
        _this.$value.html(_this.$el.val());
      });
    }
  }

  $.fn[plugin_name] = initPlugin(formRangePlugin, plugin_name);
})(jQuery);


// #############################################################################
// FORM: HTML (TinyMCE)

function initHtmlTextarea ($parent = $body) {
  const $textareas = $("[data-html-textarea]", $parent);

  $textareas.each(function (index) {
    const $textarea = $textareas.eq(index);
    let $tinymce = $textarea.tinymce();

    if ($tinymce) {
      $tinymce.remove();
    }

    let language = $html.attr("lang");

    if (language.indexOf("-") === 2) {
      language = language.split("-");
      language = language[0] + "_" + language[1].toUpperCase();
    }

    $textarea.tinymce({
      branding: false,
      content_css: "/static/css/tinymce.min.css",
      height: 250,
      inline_styles: false,
      language: language,
      menubar: false,
      mode: "specific_textareas",
      plugins: "autolink contextmenu link lists spellchecker wordcount",
      toolbar: "styleselect | bold | numlist | bullist | link | undo redo cut copy paste pastetext | removeformat",
      style_formats: [
        {
          title: "Paragraph",
          block: "p",
        },
        {
          title: "Header 2",
          block: "h2",
        },
        {
          title: "Header 3",
          block: "h3",
        },
        {
          title: "Header 4",
          block: "h4",
        },
      ],
      valid_elements: "h2,h3,h4,a,p,strong,li,ul,ol",
      valid_styles: "+a[id|rel|",
      setup: function ($editor) {
        const $textarea = $("#" + $editor.id);

        if ($textarea.attr("disabled")) {
          $editor.settings.readonly = true;
        }
      },
    });

    $tinymce = $textarea.tinymce();

    $tinymce.on("change", function () {
      tinymce.triggerSave();
    });

    $tinymce.on("focus", function () {
      const $textarea = $("#" + $tinymce.id);
      const $container = $(".mce-tinymce", $textarea.parents(".form-group"));

      $container.addClass("focus");
    });

    $tinymce.on("blur", function () {
      const $textarea = $("#" + $tinymce.id);
      const $container = $(".mce-tinymce", $textarea.parents(".form-group"));

      $container.removeClass("focus");
    });
  });

  // Workarround: https://stackoverflow.com/questions/18111582/tinymce-4-links-plugin-modal-in-not-editable

  $(document).on("focusin", function (event) {
    if ($(event.target).closest(".mce-window").length) {
      event.stopImmediatePropagation();
    }
  });
}


// #############################################################################
// FORM: AJAX UPLOAD

/**
 * Initial:
 *
 * $("[data-ajax-upload]").ajaxUpload({
 *  addExtraData: function ($upload, $form_data) {
 *    // $upload = jQuery object from the [data-ajax-upload]
 *    // $form_data = uploaded FormData
 *  },
 *  onUploadCompleted: function ($upload, $data) {
 *    // $upload = jQuery object from the [data-ajax-upload]
 *    // $data = JSON response
 *  },
 * });
 *
 * Reset:
 *
 * $("[data-ajax-upload]").ajaxUpload("reset");
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "ajaxUpload";

  const $defaults = {
    addExtraData: function ($upload, $form_data) {
      return $form_data;
    },
    onUploadCompleted: function ($upload, $data) {
    },
  };

  class ajaxUploadPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.$input = $("input[type=file]", this.$el);
      this.$button = $("button", this.$el);
      this.$progress_items = $("[data-progress-items]", this.$el);

      this.init();
    }

    init () {
      const _this = this;

      this.$input.on("change", function () {
        _this.$files = this.files;

        _this._initProgressBar();
        _this._updateButton();
      });

      this.$button.on("click", function () {
        if (_this.$files.length > 0) {
          _this.$button.addClass("disabled");
          _this.$input.attr("disabled", "disabled");

          $.each(_this.$files, function (index) {
            let $form_data = new FormData();
            const $file = _this.$files[index];

            $form_data = _this.$settings.addExtraData(_this.$el, $form_data);
            $form_data.append("file", $file);

            $.ajax({
              contentType: false,
              data: $form_data,
              processData: false,
              type: "POST",
              url: _this.$el.data("ajax-upload"),
              success: function ($data) {
                _this.$button.addClass("disabled");
                _this.$input.removeAttr("disabled");

                _this._clearInput();

                _this.$settings.onUploadCompleted(_this.$el, $data);
              },
              xhr: function () {
                return _this._updateProgressBar($file);
              },
            });
          });
        }

        return false;
      });
    }

    reset () {
      const _this = this;

      _this._clearInput();
      _this.$progress_items.attr("hidden", "hidden");
    }

    _clearInput () {
      const _this = this;

      bsCustomFileInput.destroy();
      _this.$input.val("");
      bsCustomFileInput.init();
    }

    _updateButton () {
      const _this = this;

      if (_this.$files.length > 0 && !_this.$input.hasClass("is-invalid")) {
        _this.$button.removeClass("disabled");
      } else {
        _this.$button.addClass("disabled");
      }
    }

    _initProgressBar () {
      const _this = this;

      if (!_this.progress_item) {
        const $progress_item = $("[data-progress-item]", _this.$progress_items);
        _this.progress_item = $progress_item.parent().html();
      }

      _this.$progress_items.empty();

      if (_this.$files.length > 0 && !this.$input.hasClass("is-invalid")) {
        _this.$progress_items.removeAttr("hidden");

        $.each(_this.$files, function (index) {
          const $file = _this.$files[index];

          const $item = $(_this.progress_item.replace(
            "%filename", $file.name
          ).replace(
            "%filesize", formatFileSize($file.size, 2)
          ).replace(
            "data-progress-item=\"\"", "data-progress-item=\"" + $file.name + "\""
          ));

          _this.$progress_items.append($item);
        });
      } else {
        _this.$progress_items.attr("hidden", "hidden");
      }
    }

    _updateProgressBar ($file) {
      const _this = this;

      const $xhr = $.ajaxSettings.xhr();
      const $item = $("[data-progress-item=\"" + $file.name + "\"]", _this.$el);
      const $progress_bar = $("[data-progress-bar]", $item);
      const $current_file_size = $("[data-current-file-size]", $item);
      const $cancel_upload = $("[data-cancel-upload]", $item);
      const $upload_finished = $("[data-upload-finished]", $item);

      $xhr.upload.addEventListener("progress", function (event) {
        if (event.lengthComputable) {
          const max = event.total;
          const current = event.loaded;
          const percentage = (current * 100) / max;

          $progress_bar.css("width", percentage + "%");
          $progress_bar.attr("aria-valuenow", percentage);
          $current_file_size.html(formatFileSize(current));
        }
      }, false);

      $xhr.upload.addEventListener("loadstart", function () {
        $cancel_upload.removeClass("invisible");
      });

      $xhr.upload.addEventListener("load", function () {
        $cancel_upload.remove();
        $upload_finished.removeClass("d-none");
      });

      $xhr.upload.addEventListener("abort", function () {
        const $items = $("[data-progress-item]", _this.$progress_items).not($item);

        $item.remove();

        if ($items.length === 0) {
          _this.$input.removeAttr("disabled");
          _this.reset();
        }
      });

      $cancel_upload.on("click", function () {
        $xhr.abort();
        return false;
      });

      return $xhr;
    }
  }

  $.fn[plugin_name] = initPlugin(ajaxUploadPlugin, plugin_name);
})(jQuery);


// #############################################################################
// FORM: VALIDATION

/**
 * Initial:
 *
 * $("[data-form]").formValidation({
 *  beforeSubmit: function ($form) {
 *    // $form = jQuery object from the <form>
 *  },
 *  afterSubmit: function (request, $form, $data) {
 *    // request = post request object
 *    // $form = jQuery object from the <form>
 *    // $data = JSON response
 *  },
 * });
 *
 * Reset:
 *
 * $("[data-form]").formValidation("reset");
 *
 * Destroy:
 *
 * $("[data-form]").formValidation("destroy");
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "formValidation";

  const $defaults = {
    beforeSubmit: function ($form) {
    },
    afterSubmit: function (request, $form, $data) {
    },
  };

  class formValidationPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.prefix = this.$el.data("form");
      this.$submit_button = $("button[type=\"submit\"]", this.$el);
      this.$validate_buttons = $("[data-validate]", this.$el);
      this.$html_textareas = $("[data-html-textarea]", this.$el);
      this.$formsets = $("[data-form-set]", this.$el);

      this.$form_errors = $("[data-form-errors]", this.$el);
      this.$form_errors_anchor = $("[data-form-errors-anchor]", this.$el);

      this.init();
    }

    init () {
      const _this = this;

      // Validate before submit

      _this.$el.on("blur input", ":input:not(button)", function () {
        const $input = $(this);

        _this._validateInput($input);
      });

      // Validate before submit (HTML, TinyMCE)

      _this.$html_textareas.each(function (index) {
        const $textarea = _this.$html_textareas.eq(index);
        const $tinymce = $textarea.tinymce();

        if ($tinymce) {
          $tinymce.on("blur change", function () {
            const $hidden_textarea = $($tinymce.targetElm);

            _this._validateInput($hidden_textarea);
          });
        }
      });

      // Validate buttons

      _this.$validate_buttons.on("click", function () {
        const index = _this.$validate_buttons.index(this);
        const $validate_button = _this.$validate_buttons.eq(index);

        _this.response_type = $validate_button.data("response-type");

        _this._validateInputs();

        if (_this._checkFormValidity()) {
          _this.$el.data("form-is-invalid", false);
        } else {
          _this.$el.data("form-is-invalid", true);
        }

        return false;
      });

      // Validate after submit

      _this.$submit_button.on("click", function () {
        const index = _this.$submit_button.index(this);
        const $this = _this.$submit_button.eq(index);

        _this.submit_name = $this.attr("name");
        _this.submit_value = $this.attr("value");
      });

      _this.$el.on("submit", function () {
        _this.$settings.beforeSubmit(_this.$el);

        _this._validateInputs();

        if (_this._checkFormValidity()) {
          _this._ajaxSubmit();
        }

        return false;
      });
    }

    reset () {
      const _this = this;

      $(":input:not(button)", _this.$el).each(function () {
        const $input = $(this);

        _this._removeErrorMessage($input);
        $input.val("");
      });
    }

    _addRequirements ($inputs) {
      const $abbr = $(".label abbr", $inputs.parents(".form-group"));

      if (!$abbr.hasClass("d-none")) {
        return;
      }

      $abbr.removeClass("d-none");

      if (!$inputs.is(":checkbox") && $inputs.length === 1) {
        $inputs.attr("required", "required");
      }

      $inputs.parents("[data-field-hidden]").removeClass("d-none");
      $inputs.parents("[data-fieldset-hidden]").removeClass("d-none");
    }

    _removeRequirements ($inputs) {
      const _this = this;
      const $abbr = $(".label abbr", $inputs.parents(".form-group"));

      if ($abbr.hasClass("d-none")) {
        return;
      }

      $abbr.addClass("d-none");

      if (!$inputs.is(":checkbox") && $inputs.length === 1) {
        $inputs.removeAttr("required");
        $inputs.removeClass("is-invalid");
      }

      $inputs.parents("[data-field-hidden]").addClass("d-none");

      // Hide fieldset only if no requirements exists
      const $fieldset_hidden = $inputs.parents("[data-fieldset-hidden]");
      const $abbrs = $(".label abbr:not(.d-none)", $fieldset_hidden);

      if ($abbrs.length === 0) {
        $inputs.parents("[data-fieldset-hidden]").addClass("d-none");
      }

      _this._removeErrorMessage($inputs);
    }

    _updateRequirements ($requirements) {
      const _this = this;

      $.each($requirements, function (field_name, required) {
        if (_this.prefix) {
          field_name = _this.prefix + "-" + field_name;
        }

        const $inputs = $("[name=\"" + field_name + "\"]");

        if (required) {
          _this._addRequirements($inputs);
        } else {
          _this._removeRequirements($inputs);
        }
      });
    }

    _inputIsVisible ($input) {
      return $input.is(":visible") || ($input.data("html-textarea") && $input.prev(".mce-tinymce").is(":visible"));
    }

    _checkValidity ($input) {
      const _this = this;

      let is_valid = true;
      let is_readonly = false;

      if (_this._inputIsVisible($input)) {
        if ($input.attr("readonly")) {
          // Workaround: checkValidity() not work on readonly inputs
          is_readonly = true;
          $input.removeAttr("readonly");
        }

        if (!$input[0].checkValidity()) {
          is_valid = false;
        }

        if (is_readonly) {
          $input.attr("readonly", "");
        }
      }

      return is_valid;
    }

    _checkFormValidity () {
      const _this = this;
      let is_valid = true;

      $(":input:not(button)", _this.$el).each(function () {
        const $input = $(this);

        is_valid = _this._checkValidity($input);

        if (!is_valid) {
          return false;
        }
      });

      return is_valid;
    }

    _validateData ($data, $input, auto_focus = false) {
      const _this = this;

      let is_valid_input_file = true;

      if ($input.is(":file")) {
        is_valid_input_file = _this._validateInputFile($input);
      }

      if (_this._checkValidity($input) && is_valid_input_file) {
        _this._removeErrorMessage($input);
      }

      _this._insertErrorMessage($input, $data.errors);
      _this._updateRequirements($data.requirements);
      _this._focusInput(auto_focus);
    }

    _validateInputFile ($input) {
      const _this = this;
      const $files = $input[0].files;
      const max_size = $input.data("max-size");

      let sizes = 0;

      if ($files.length === 0) {
        return true;
      }

      $.each($files, function (index) {
        sizes += $files[index].size;
      });

      if (sizes > max_size) {
        const input_name = $input.attr("name");
        const $errors = {};

        $errors[input_name] = [
          gettext("Please keep filesize under %max_upload_size. Current filesize is %size.").replace(
            "%max_upload_size", formatFileSize(max_size)
          ).replace(
            "%size", formatFileSize(sizes)
          ),
        ];

        _this._insertErrorMessage($input, $errors);

        return false;
      }

      return true;
    }

    _validateInput ($input) {
      const _this = this;

      $.ajax({
        contentType: false,
        data: new FormData(_this.$el[0]),
        processData: false,
        type: "POST",
        url: _this.$el.attr("action"),
        success: function ($data) {
          _this._validateData($data, $input, false);
        },
      });
    }

    _validateInputs () {
      const _this = this;
      const $inputs = [];

      $(":input:not(button)", _this.$el).each(function () {
        const $input = $(this);

        if (_this._inputIsVisible($input)) {
          $inputs.push($input);
        }
      });

      $.ajax({
        contentType: false,
        data: new FormData(_this.$el[0]),
        processData: false,
        type: "POST",
        url: _this.$el.attr("action"),
        success: function ($data) {
          _this._updateFormsetErrorMessages($data.errors);

          $.each($inputs, function (index, $input) {
            _this._validateData($data, $input, true);
          });
        },
      });
    }

    _updateFormErrorMessages ($errors) {
      const _this = this;

      if (!$errors) {
        return;
      }

      if ($errors.__all__) {
        _this.$form_errors.html($errors.__all__);
        _this.$form_errors.removeClass("d-none");
      } else {
        _this.$form_errors.empty();
        _this.$form_errors.addClass("d-none");
      }
    }

    _updateFormsetErrorMessages ($errors) {
      const _this = this;

      _this.$formsets.each(function (index) {
        const $formset = _this.$formsets.eq(index);
        const $label = $("[data-form-set-label]", $formset);
        const $error = $("[data-form-set-error]", $formset);
        const error = $errors[$error.attr("id").replace("_error", "")] || "";

        $error.html(error);

        if (error) {
          $label.addClass("is-invalid");
          $error.focus();
        } else {
          $label.removeClass("is-invalid");
        }
      });
    }

    _insertErrorMessage ($input, $errors) {
      const _this = this;

      if (!$errors) {
        return;
      }

      const input_name = $input.attr("data-name") || $input.attr("name");
      const errors = $errors[input_name.replace(_this.prefix + "-", "")];

      if (errors) {
        const $error = $("#id_" + input_name + "_error");
        const $input_wrapper = $input.parents(".input-wrapper");

        $input_wrapper.addClass("is-invalid");

        if ($input.is(":checkbox") || $input.is(":radio")) {
          $input = $("[name=" + input_name + "]");
        }

        if ($input.attr("data-html-textarea")) {
          $input = $(".mce-tinymce", $input.parents(".form-group"));
        }

        if ($input_wrapper.length > 0) {
          $(":input", $input_wrapper).addClass("is-invalid");
        } else {
          $input.addClass("is-invalid");
        }

        $error.html(errors);
      }
    }

    _removeErrorMessage ($input) {
      const input_name = $input.data("name") || $input.attr("name");
      const $input_wrapper = $input.parents(".input-wrapper");

      $input_wrapper.removeClass("is-invalid");

      if ($input.is(":checkbox") || $input.is(":radio")) {
        $input = $("[name=" + input_name + "]");
      }

      if ($input.data("html-textarea")) {
        $input = $(".mce-tinymce", $input.parents(".form-group"));
      }

      if ($input_wrapper.length > 0) {
        $(":input", $input_wrapper).removeClass("is-invalid");
      } else {
        $input.removeClass("is-invalid");
      }
    }

    _focusInput (auto_focus) {
      const _this = this;

      if (auto_focus) {
        if (_this.$form_errors.is(":visible")) {
          _this.$form_errors_anchor.focus();
        } else {
          const $is_invalid = $(".is-invalid", _this.$el);
          const $focus_input = $is_invalid.first();

          if ($focus_input.is(":input")) {
            $focus_input.focus();
          } else {
            $(":input", $focus_input).first().focus();
          }
        }
      }
    }

    _ajaxSubmit () {
      const _this = this;
      const $form_data = new FormData(_this.$el[0]);

      $form_data.append("submit", 1);

      if (_this.submit_name && _this.submit_value) {
        $form_data.append(_this.submit_name, _this.submit_value);
      }

      if (_this.response_type) {
        $form_data.append("response_type", _this.response_type);
      }

      _this.$submit_button.addClass("btn-loader");

      const $ajax_settings = {
        contentType: false,
        data: $form_data,
        processData: false,
        type: "POST",
        url: _this.$el.attr("action"),
        success: function ($data, textStatus, request) {
          _this._updateFormErrorMessages($data.errors);
          _this._focusInput(true);

          _this.$submit_button.removeClass("btn-loader");
          _this.$settings.afterSubmit(request, _this.$el, $data);
        },
      };

      if (_this.response_type) {
        $ajax_settings.xhrFields = {
          responseType: _this.response_type,
        };
      }

      $.ajax($ajax_settings);
    }
  }

  $.fn[plugin_name] = initPlugin(formValidationPlugin, plugin_name);
})(jQuery);


// #############################################################################
// FORM: WIZARD

/**
 * Initial:
 *
 * $("[data-form-wizard]").formWizard();
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "formWizard";

  const $defaults = {};

  class formWizardPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.$steps = $("[data-step]", this.$el);
      this.$tabs = $("[data-tab]", this.$el);
      this.$select = $("[data-select]", this.$el);
      this.$summary = $("[data-summary]", this.$el);
      this.$previous = $("[data-previous]", this.$el);
      this.$next = $("[data-next]", this.$el);
      this.$submit = $("[data-submit]", this.$el);
      this.current_tab = 0;

      this.init();
    }

    init () {
      const _this = this;

      _this._initSummary();

      _this.$previous.on("click", function () {
        _this._changeTab(-1);
        return false;
      });

      _this.$next.on("click", function () {
        _this._changeTab(1);
        return false;
      });

      _this.$select.on("click", function () {
        const index = _this.$select.index(this);
        const $show = _this.$select.eq(index);

        if (!_this.$el.data("form-is-invalid")) {
          _this._updateSummary();

          _this.$tabs.removeClass("active");
          _this.current_tab = index;

          _this._showStep();
          _this._updateButtons();
          _this._updateNav();

          $show.tab("show");
        }

        return false;
      });
    }

    _changeTab (direction) {
      const _this = this;

      if (!_this.$el.data("form-is-invalid")) {
        _this._updateSummary();

        _this.$tabs.removeClass("active");
        _this.current_tab = _this.current_tab + direction;

        _this._showStep();
        _this._updateButtons();
        _this._updateNav();
      }
    }

    _showStep () {
      const _this = this;

      _this.$steps.addClass("d-none");
      _this.$steps.eq(_this.current_tab).removeClass("d-none");
    }

    _updateButtons () {
      const _this = this;
      const $current_tab = _this.$tabs.eq(_this.current_tab);

      $current_tab.addClass("active");

      if (_this.$previous.length === 0 || _this.$next.length === 0) {
        return;
      }

      if (_this.current_tab === 0) {
        _this.$previous.addClass("d-none");
        _this.$previous.removeClass("d-flex");
      } else {
        _this.$previous.addClass("d-flex");
        _this.$previous.removeClass("d-none");
      }

      if (_this.current_tab === _this.$tabs.length - 1) {
        _this.$next.addClass("d-none");
        _this.$next.removeClass("d-flex");
        _this.$submit.addClass("d-flex");
        _this.$submit.removeClass("d-none");
      } else {
        _this.$next.addClass("d-flex");
        _this.$next.removeClass("d-none");
        _this.$submit.addClass("d-none");
        _this.$submit.removeClass("d-flex");
      }
    }

    _updateNav () {
      const _this = this;

      const $current_nav_item = _this.$select.eq(_this.current_tab);

      _this.$select.removeClass("active");
      _this.$select.attr("aria-selected", "false");

      $current_nav_item.removeClass("disabled");
      $current_nav_item.removeAttr("tabindex");
      $current_nav_item.addClass("active");
      $current_nav_item.attr("aria-selected", "true");
      $current_nav_item.removeAttr("aria-disabled");
    }

    _initSummary () {
      const _this = this;

      if (_this.$summary.length === 0) {
        return;
      }

      const $summary_items = $("[data-summary-items]", _this.$summary);

      _this.summary_item_template = $summary_items.html();

      $("[data-summary-item]", $summary_items).remove();

      _this.summary_step_template = _this.$summary.html();

      _this.$summary.empty();
      _this.$summary.removeAttr("hidden");
    }

    _getSelectValue ($inputs, value) {
      const $options = $("option:selected", $inputs);

      $options.each(function (index) {
        const $option = $options.eq(index);

        if (index > 0) {
          value += "<br>";
        }

        value += $option.text().trim();
      });

      return value;
    }

    _getFileValue ($inputs, value) {
      $.each($inputs.prop("files"), function (index, file) {
        if (index > 0) {
          value += "<br>";
        }

        value += file.name;
      });

      return value;
    }

    _getCheckboxRadioValue ($input, value) {
      const id = $input.attr("id");
      const $label = $("label[for=\"" + id + "\"]").clone();

      $("*", $label).remove();
      value += $label.text().trim();

      return value;
    }

    _addInputGroupText ($input, value) {
      const $input_group = $input.parents(".input-group");
      const append = $(".input-group-append", $input_group).text();
      const prepend = $(".input-group-prepend", $input_group).text();

      if (append) {
        value = value + " " + prepend;
      }

      if (prepend) {
        value = append + " " + value;
      }

      return value;
    }

    _updateSummary () {
      const _this = this;

      if (_this.$summary.length === 0) {
        return;
      }

      const $current_tab = _this.$tabs.eq(_this.current_tab);
      const $summary_step = $("[data-summary-step=\"" + _this.current_tab + "\"]", _this.$el);
      const $inputs = $(":input:visible:not(button):not([data-summary-hidden=\"1\"])", $current_tab);
      let summary_html = "";

      if ($inputs.length === 0) {
        return;
      }

      const $form_groups = $(".form-group", $current_tab);

      $form_groups.each(function (index) {
        const $form_group = $form_groups.eq(index);
        const $inputs = $(":input:visible:not(button)", $form_group);
        const $label = $(".label, label", $form_group).first().clone();

        $("*", $label).remove();

        const label = $label.text().trim();
        let value = "";

        if ($inputs.length === 1) {
          let input_value = $inputs.val();

          if ($inputs.is("select")) {
            value = _this._getSelectValue($inputs, value);
          } else if ($inputs.is(":checkbox")) {
            if ($inputs.is(":checked")) {
              value = gettext("Yes");
            } else {
              value = gettext("No");
            }
          } else if ($inputs.is(":file")) {
            value = _this._getFileValue($inputs, value);
          } else {
            if (input_value) {
              input_value = _this._addInputGroupText($inputs, input_value);
            }

            value = escapeText(input_value);
          }
        } else {
          $inputs.each(function (index) {
            const $input = $inputs.eq(index);

            if ($input.is(":checkbox") || $input.is(":radio")) {
              if (index > 0) {
                value += "<br>";
              }

              value += _this._getCheckboxRadioValue($input, value);
            } else {
              if (index > 0) {
                value += " ";
              }

              value += escapeText($input.val());
            }
          });
        }

        if (value.trim()) {
          const summary_item_html = _this.summary_item_template.replace(
            "%name", $inputs.attr("name")
          ).replace(
            "%label", label
          ).replace(
            "%value", value
          );

          summary_html += summary_item_html;
        }
      });

      if ($summary_step.length === 0) {
        const $step = _this.$steps.eq(_this.current_tab);

        const $new_summary_step = $(_this.summary_step_template.replace(
          "%step_index", _this.current_tab
        ).replace(
          "%step", $step.text()
        ));

        $("[data-summary-items]", $new_summary_step).html(summary_html);

        _this.$summary.append($new_summary_step);
      } else {
        $("[data-summary-items]", $summary_step).html(summary_html);
      }
    }
  }

  $.fn[plugin_name] = initPlugin(formWizardPlugin, plugin_name);
})(jQuery);


// #############################################################################
// FORM: FILE TREE

/**
 * Initial:
 *
 * $("[data-file-tree]").formFileTree()
 *
 * Reload:
 *
 * $("[data-file-tree]").formFileTree("reload");
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "formFileTree";

  const $defaults = {};

  class formFileTreePlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.$container = this.$el.parents(".file-tree");
      this.$accept_extensions = this.$el.data("accept-extensions");
      this.accept_folder = this.$el.data("accept-folder");
      this.path = this.$el.data("file-tree");
      this.root = this.$el.data("root");
      this.$input = $("input", this.$el.parents(".form-group"));

      this.init();
    }

    init () {
      const _this = this;

      _this._showTree(_this.$el, _this.root);

      _this.$el.on("click", "a", function () {
        const $a = $(this);
        const $li = $a.parent("li");
        const $ul = $("ul", $li);

        $("a", _this.$el).removeClass("selected");
        $a.addClass("selected");

        if ($li.hasClass("directory")) {
          $ul.remove();

          if ($li.hasClass("collapsed")) {
            $li.removeClass("collapsed");
            $li.addClass("expanded");

            _this._showTree($li, $a.data("item").match(/.*\//));
          } else {
            $li.removeClass("expanded");
            $li.addClass("collapsed");
          }
        }

        _this._setInputValue($a);

        return false;
      });
    }

    reload ($args) {
      const _this = this;

      _this.selected_item = $args.path;

      let path = _this.selected_item.slice(_this.root.length);
      path = path.match(/.*\//)[0];

      const index = 1;
      const $path = path.split("/");
      const $item = _this._getItem($path, index);

      $("ul", $item[0]).remove();

      _this._showTree($item[0], $item[1], $path, index);
    }

    _setInputValue ($a) {
      const _this = this;
      const item = $a.data("item");

      _this.$input.val("");
      _this.$input.removeClass("is-invalid");

      if (item) {
        if (item.endsWith("/")) {
          if (_this.accept_folder === 1) {
            _this.$input.val(item);
          }
        } else {
          const $ext = item.split(".");

          if ($ext.length > 1) {
            const ext = "." + $ext[$ext.length - 1];

            if (_this.$accept_extensions && _this.$accept_extensions.indexOf(ext) > -1) {
              _this.$input.val(item);
            }
          }
        }
      }
    }

    _getItem ($path, index) {
      const _this = this;
      const $current_path = $path.slice(0, index);
      const data_item = _this.root + $current_path.join("/") + "/";
      let $li = $("[data-item=\"" + data_item + "\"]", _this.$container).parent("li");

      if (!$li.length) {
        $li = this.$el;
      }

      if (index > 0) {
        $li.removeClass("collapsed");
        $li.addClass("expanded");
      }

      return [$li, data_item];
    }

    _scrollToSelectedItem () {
      const _this = this;
      const $a = $("[data-item=\"" + _this.selected_item + "\"]");

      if ($a.length > 0) {
        $a.addClass("selected");

        _this._setInputValue($a);

        _this.$el.scrollTop(_this.$el.scrollTop() + $a.position().top);

        _this.$container.scrollTop(
          $a.position().top - parseInt(_this.$container.css("padding-top"))
        );
      }
    }

    _showTree ($el, dir, $path, index) {
      const _this = this;

      $.post(_this.path, {
        dir: escape(dir),
      }, function (html) {
        $el.append(html);

        if ($path) {
          if (index === $path.length - 1) {
            _this._scrollToSelectedItem();
          }

          if (index < $path.length - 1) {
            index += 1;

            const $item = _this._getItem($path, index);

            _this._showTree($item[0], $item[1], $path, index);
          }
        }
      });
    }
  }

  $.fn[plugin_name] = initPlugin(formFileTreePlugin, plugin_name);
})(jQuery);


// #############################################################################
// AJAX MODAL

/**
 * Initial:
 *
 * $("body").ajaxModal({
 *  selector: "[data-modal-link]",
 *  beforeModalOpen: function ($modal, $data) {
 *    // $modal = jQuery object from the <div data-modal>
 *    // $data = JSON response
 *  },
 *  onModalOpen: function ($modal, $data) {
 *    // $modal = jQuery object from the <div data-modal>
 *    // $data = JSON response
 *  },
 *  onModalClose: function ($modal) {
 *    // $modal = jQuery object from the <div data-modal>
 *  },
 * });
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "ajaxModal";

  const $defaults = {
    selector: "[data-modal-link]",
    beforeModalOpen: function ($modal, $data) {
    },
    onModalOpen: function ($modal, $data) {
    },
    onModalClose: function ($modal) {
    },
  };

  class ajaxModalPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.el = $element;

      this.$el = $($element);
      this.$modal_wrapper = $("#modal_wrapper");

      this.init();
    }

    init () {
      const _this = this;

      _this.$el.on("click", _this.$settings.selector, function () {
        $.ajax({
          url: this.href,
          success: function ($data) {
            _this.$modal_wrapper.empty().html($data);

            const $modal = $("[data-modal]", _this.$modal_wrapper);

            $modal.modal();

            _this.$settings.beforeModalOpen($modal, $data);

            $modal.on("shown.bs.modal", function () {
              _this.$settings.onModalOpen($modal, $data);
            });

            $modal.on("hidden.bs.modal", function () {
              _this.$settings.onModalClose($modal);
              _this.$modal_wrapper.empty();
            });
          },
        });

        return false;
      });
    }
  }

  $.fn[plugin_name] = initPlugin(ajaxModalPlugin, plugin_name);
})(jQuery);


// #############################################################################
// DATA TABLE

/**
 * Initial:
 *
 * $("[data-table]").xDataTable({
 *  options: {
 *    // Documentation https://datatables.net/reference/option/
 *  },
 *  onInit: function ($table, $json) {
 *    // $table = jQuery object from the [data-table]
 *    // $json = JSON data retrieved from the server, if Ajax loading data
 *  },
 *  onStateLoaded: function ($table, $data) {
 *    // $table = jQuery object from the [data-table]
 *    // $data = State information read from storage
 *  },
 *  onDraw: function ($table) {
 *    // $table = jQuery object from the [data-table]
 *  },
 *  customizeCSV: function (csv) {
 *    // csv = CSV data
 *  }
 * });
 *
 * Reload:
 *
 * $("[data-table]").xDataTable("reload");
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "xDataTable";

  const $defaults = {
    options: {},
    buttons: {},
    onInit: function ($table, $json) {
    },
    onStateLoaded: function ($table, $data) {
    },
    onDraw: function ($table) {
    },
    customizeCSV: function (csv) {
      return csv;
    },
  };

  class xDataTablePlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.$element = $element;

      this.$fields = JSON.parse($element.getAttribute("data-fields"));
      this.url = $element.getAttribute("data-table");
      this.csfr_token = $element.getAttribute("data-csrf-token");

      this.$buttons = $("[data-button=\"" + $element.id + "\"]");
      this.$reset = $("[data-reset=\"" + $element.id + "\"]");
      this.$filter = $("[data-filter=\"" + $element.id + "\"]");
      this.$filter_counter = $("[data-filter-counter=\"" + $element.id + "\"]");

      this.$inputs = $("[data-input]", this.$filter);
      this.$selects = $("[data-select]", this.$filter);

      this.$processing = $("[data-processing]", $element);
      this.$last_updated = $("[data-last-updated]", $element);

      this.init();
    }

    init () {
      const _this = this;

      if (!$.fn.dataTable) {
        return;
      }

      $.fn.dataTable.ext.errMode = "throw";

      _this._setClasses();

      const $defaults = _this._initDefaults();

      _this.$api = _this.$el.DataTable($defaults);

      _this._hideColumns();
      _this._initButtons();
      _this._initFilters();
      _this._initEventListener();
      _this._checkFilters();
    }

    reload ($args) {
      const _this = this;
      const top = $(window).scrollTop();

      if ($args) {
        const url = $args.url;

        if (url) {
          _this.$api.ajax.url(url);
        }
      }

      _this.$api.ajax.reload(function () {
        $(window).scrollTop(top);
      }, false);
    }

    _autoReload () {
      const _this = this;
      const autoreload = _this.$el.data("autoreload");

      if (autoreload) {
        setInterval(function () {
          _this.reload();
        }, autoreload);
      }
    }

    _restoreColumsClass () {
      const _this = this;
      const column_classes = [];

      _this.$api.rows().every(function (index) {
        const $row = _this.$api.row(index).nodes();
        const $columns = $("td", $row);
        const column_class = [];

        $columns.each(function (index) {
          const $column = $columns.eq(index);

          column_class.push($column.attr("class"));
        });

        column_classes.push(column_class);
      });

      _this.$api.one("draw.dtr", function () {
        _this.$api.rows().every(function (index) {
          const $row = _this.$api.row(index).nodes();
          const $columns = $("td", $row);
          const column_class = column_classes[index];

          if (column_class) {
            $columns.each(function (index) {
              const $column = $columns.eq(index);

              $column.attr("class", column_class[index]);
            });
          }
        });
      });
    }

    _hideColumns () {
      const _this = this;

      for (let i = 0; i < _this.$fields.length; i++) {
        if (_this.$fields[i].hide) {
          _this.$api.column(i).visible(false);
        }
      }
    }

    _initEventListener () {
      const _this = this;

      _this.$api.on("init", function (event, $settings, $json) {
        _this._lastUpdated();

        _this.$settings.onInit(_this.$el, $json);
      });

      _this.$api.on("stateLoaded", function (event, $settings, $data) {
        _this.$settings.onStateLoaded(_this.$el, $data);
      });

      _this.$api.on("draw", function (event, $settings) {
        _this.$settings.onDraw(_this.$el);
      });

      _this.$api.on("preXhr.dtr", function () {
        _this._restoreColumsClass();
      });

      _this.$api.on("processing.dt", function (event, $settings, processing) {
        _this._processingIndicator(processing);
      });
    }

    _processingIndicator (processing) {
      const _this = this;

      if (processing) {
        _this._lastUpdated();
        _this.$processing.removeClass("d-none");
      } else {
        _this.$processing.addClass("d-none");
      }
    }

    _lastUpdated () {
      const _this = this;

      if (_this.$last_updated.length === 0) {
        return;
      }

      const text = _this.$last_updated.data("text");
      const text_plural = _this.$last_updated.data("text-plural");
      let seconds = 1;

      clearInterval(_this.last_updated);

      _this.$last_updated.text(
        text.replace("[seconds]", seconds)
      );

      _this.last_updated = setInterval(function () {
        seconds += 1;

        _this.$last_updated.text(
          text_plural.replace("[seconds]", seconds)
        );
      }, 1000);
    }

    _defaultButtons () {
      const _this = this;

      const $buttons = [];

      if (_this.$element.hasAttribute("data-export-csv")) {
        $buttons.push({
          extend: "csv",
          exportOptions: {
            columns: "thead th:not(.no-export-csv)",
          },
          customize: function (csv) {
            return _this.$settings.customizeCSV(csv);
          },
        });
      }

      $.merge($buttons, _this.$settings.buttons);

      return $buttons;
    }

    _initButtons () {
      const _this = this;

      _this.$buttons.on("click", function () {
        const button_action = this.getAttribute("data-button-action");

        $("." + button_action).click();
      });
    }

    _initDefaults () {
      const _this = this;

      const $defaults = {
        autoWidth: false,
        ajax: {
          beforeSend: function ($xhr) {
            $xhr.setRequestHeader("X-CSRFToken", _this.csfr_token);
          },
          type: "POST",
          url: _this.url,
        },
        buttons: {
          buttons: _this._defaultButtons(),
        },
        columnDefs: [
          {
            sortable: false,
            targets: "no-sort",
          },
        ],
        language: {
          sEmptyTable: gettext("No data available"),
          sInfo: gettext("Showing _START_ to _END_ of _TOTAL_ entries"),
          sInfoEmpty: gettext("Showing 0 to 0 of 0 entries"),
          sInfoThousands: ".",
          sLengthMenu: gettext("Show _MENU_ entries"),
          sProcessing: gettext("Please wait ..."),
          sZeroRecords: gettext("No matching entries found"),
          paginate: {
            next: gettext("Next"),
            previous: gettext("Previous"),
          },
          aria: {
            sortAscending: gettext(": activate to sort column ascending"),
            sortDescending: gettext(": activate to sort column descending"),
          },
        },
        lengthMenu: [
          [10, 50, 100, -1],
          [10, 50, 100, gettext("All")],
        ],
        ordering: true,
        pagingType: "simple_numbers",
        processing: true,
        serverSide: true,
        stateSave: true,
        stateLoaded: function ($settings, $data) {
          _this._setStateFilters($data);
        },
        initComplete: function () {
          _this._autoReload();
        },
      };

      _this.$settings.options.columns = _this._loadDynamicFields();

      $.extend($defaults, _this.$settings.options);

      return $defaults;
    }

    _checkFilters () {
      const _this = this;

      const $input_values = _this.$inputs.filter(function () {
        return $(this).val();
      });

      const $select_values = _this.$selects.filter(function () {
        return $(this).val();
      });

      if ($input_values.length > 0 || $select_values.length > 0) {
        _this.$filter_counter.text(
          $input_values.length + $select_values.length
        );

        _this.$reset.removeClass("disabled");
      } else {
        _this.$filter_counter.empty();
        _this.$reset.addClass("disabled");
      }
    }

    _initFilters () {
      const _this = this;
      const $timeouts = {};

      _this.$inputs.on("input", function () {
        const index = _this.$inputs.index(this);
        const $input = _this.$inputs.eq(index);
        const $column = _this.$api.column($input.data("column"));
        const value = this.value;

        clearTimeout($timeouts[index]);

        $timeouts[index] = setTimeout(function () {
          $column.search(value).draw();
        }, 1200);

        _this._checkFilters();
      });

      _this.$selects.on("change", function () {
        const index = _this.$selects.index(this);
        const $select = _this.$selects.eq(index);
        const column = $select.data("column");
        const $column = _this.$api.column(column);

        $column.search($select.val()).draw();

        _this._checkFilters();
      });

      // Reset filters
      _this.$reset.on("click", function () {
        _this.$api.columns().search("").draw();

        _this.$inputs.val("");

        _this.$selects.each(function (index) {
          const $select = _this.$selects.eq(index);
          const value = $("[selected]", $select).val();

          if (value) {
            $select.val(value);
          } else {
            $select.val("");
          }
        });

        _this._checkFilters();

        return false;
      });
    }

    _setClasses () {
      $.fn.dataTable.ext.classes.sInfo = "dataTables_info";
      $.fn.dataTable.ext.classes.sLength = "dataTables_length";
      $.fn.dataTable.ext.classes.sLengthSelect = "custom-select";
      $.fn.dataTable.ext.classes.sPageButton = "page-item page-link";
      $.fn.dataTable.ext.classes.sPageButtonActive = "active";
      $.fn.dataTable.ext.classes.sSortAsc = "sorting-asc";
      $.fn.dataTable.ext.classes.sSortColumn = "sorting-";
      $.fn.dataTable.ext.classes.sSortDesc = "sorting-desc";
      $.fn.dataTable.ext.classes.sTable = "data-table";
    }

    _loadDynamicFields () {
      const _this = this;
      const $columns = _this.$settings.options.columns;
      const $extended_columns = [];

      for (let i = 0; i < $columns.length; i++) {
        if ($columns[i].data === "PLACEHOLDER_FIELDS") {
          for (let i = 0; i < _this.$fields.length; i++) {
            $extended_columns.push(_this.$fields[i]);
          }
        } else {
          $extended_columns.push($columns[i]);
        }
      }

      return $extended_columns;
    }

    _setStateFilters ($data) {
      // Restore saved filter values

      $.each($data.columns, function (index) {
        const $search = $data.columns[index].search;

        if ($search) {
          const search = $search.search;

          if (search) {
            $("[data-column=" + index + "]").val(search);
          }
        }
      });
    }
  }

  $.fn[plugin_name] = initPlugin(xDataTablePlugin, plugin_name);
})(jQuery);


// #############################################################################
// DOWNLOAD BLOB

/**
 * Initial:
 *
 * $("[data-download]").downloadBlob({
 *  onDownloadStarted: function ($data) {
 *    // $data = JSON response
 *  },
 * });
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "downloadBlob";

  const $defaults = {
    onDownloadStarted: function ($data) {
    },
  };

  class downloadBlobPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);

      this.init();
    }

    init () {
      const _this = this;

      _this.$el.on("click", function () {
        $.ajax({
          dataType: "json",
          type: "GET",
          url: this.href,
          success: function ($data) {
            _this.$settings.onDownloadStarted($data);

            if ($data.base64) {
              const $blob = _this._base64toBlob($data.base64, $data.content_type);
              _this._downloadBlob($blob, $data.file_name);
            }
          },
        });

        return false;
      });
    }

    _downloadBlob ($data, file_name) {
      const url = window.URL || window.webkitURL;
      const $a = $("<a>");

      $body.append($a);

      $a[0].href = url.createObjectURL($data);
      $a[0].download = file_name;
      $a[0].click();

      window.URL.revokeObjectURL(url);
      $a.remove();
    }

    _base64toBlob (data, content_type, slice_size = 512) {
      const $byte_characters = atob(data);
      const $byte = [];

      for (let offset = 0; offset < $byte_characters.length; offset += slice_size) {
        const slice = $byte_characters.slice(offset, offset + slice_size);

        const $byte_numbers = new Array(slice.length);

        for (let i = 0; i < slice.length; i++) {
          $byte_numbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array($byte_numbers);

        $byte.push(byteArray);
      }

      return new Blob($byte, {
        type: content_type,
      });
    }
  }

  $.fn[plugin_name] = initPlugin(downloadBlobPlugin, plugin_name);
})(jQuery);


// #############################################################################
// FORM SET

/**
 * Initial:
 *
 * $("[data-form-set]").formSet();
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "formSet";

  const $defaults = {};

  class formSetPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.$body = $("[data-form-set-body]", this.$el);
      this.$template = $("[data-form-set-empty-item]", this.$el).html();
      this.$add = $("[data-form-set-add]", this.$el);

      this.init();
    }

    init () {
      const _this = this;
      const prefix = _this.$el.data("form-set");

      _this.$total_forms = $("#id_" + prefix + "-TOTAL_FORMS", this.$el);
      _this.min_num_forms = parseInt($("#id_" + prefix + "-MIN_NUM_FORMS").val());
      _this.max_num_forms = parseInt($("#id_" + prefix + "-MAX_NUM_FORMS").val());

      this.$add.on("click", function () {
        _this._addFormset();

        return false;
      });

      _this.$el.on("click", "[data-form-set-delete]", function () {
        const $delete = $(this);

        _this._deleteFormset($delete);

        return false;
      });
    }

    _addFormset () {
      const _this = this;

      const counter = $("[data-form-set-item]:visible", _this.$body).length;
      const $items = $("[data-form-set-item]", _this.$body);
      const count = $items.length;
      const $new_item = $(_this.$template.replace(/__prefix__/g, count));

      _this.$body.append($new_item);

      $new_item.find(":input:visible").first().focus();
      $new_item.attr("data-form-set-item", counter);

      _this.$total_forms.val(count + 1);

      if (counter + 1 === _this.max_num_forms) {
        _this.$add.addClass("disabled");
      }

      $("[data-form-set-delete]", $new_item).removeClass("disabled");

      const $all_delete = $("[data-form-set-delete]", _this.$el);

      if (counter < _this.min_num_forms) {
        $all_delete.addClass("disabled");
      } else {
        $all_delete.removeClass("disabled");
      }
    }

    _deleteFormset ($delete) {
      const _this = this;
      const counter = $("[data-form-set-item]:visible", _this.$body).length;
      const $all_delete = $("[data-form-set-delete]", _this.$el);
      const $item = $delete.parents("[data-form-set-item]");

      if (counter - 1 === _this.min_num_forms) {
        $all_delete.addClass("disabled");
      } else {
        $all_delete.removeClass("disabled");
      }

      $(":input:visible", $item).val("");
      $item.addClass("d-none");

      if (counter - 1 < _this.max_num_forms) {
        _this.$add.removeClass("disabled");
      }

      $("[name$=\"-DELETE\"]", $item).click();
    }
  }

  $.fn[plugin_name] = initPlugin(formSetPlugin, plugin_name);
})(jQuery);


// #############################################################################
// CLIPBOARD

/**
 * Initial:
 *
 * <input id="target" value="Copy text">
 * <a data-clipboard="copy" data-clipboard-target="#target">Copy</a>
 *
 * or
 *
 * <a data-clipboard data-clipboard-text="Copy text">Copy</a>
 *
 * $("body").clipBoard({
 *  selector: "[data-clipboard]",
 *  beforeCopyText: function ($target, text) {
 *    // $target = jQuery object from [data-clipboard-target]
 *    // text = Text to be copied
 *    return text;
 *  },
 * });
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "clipBoard";

  const $defaults = {
    selector: "[data-clipboard]",
    beforeCopyText: function ($target, text) {
      return text;
    },
  };

  class clipBoardPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.el = $element;

      this.$el = $($element);
      this.$dummy = undefined;

      this.init();
    }

    init () {
      const _this = this;

      _this.$el.on("click", _this.$settings.selector, function () {
        const $this = $(this);

        const text = $this.data("clipboard-text");
        const target = $this.data("clipboard-target");

        _this.$target = $(target);

        _this.action = $this.data("clipboard");

        if (text) {
          _this.action = "copy";

          _this._fakeSelectText(text);
        } else {
          _this._selectText();
        }

        _this._copyText();
        _this._clearSelection();

        return false;
      });
    }

    _fakeSelectText (select_text) {
      const _this = this;

      select_text = _this.$settings.beforeCopyText(
        _this.$target, select_text
      );

      _this.$dummy = $("<textarea>");
      _this.$dummy.val(select_text);

      _this.$el.append(_this.$dummy);

      _this.$dummy.get(0).select();
      _this.$dummy.get(0).setSelectionRange(0, select_text.length);

      return select_text;
    }

    _selectText () {
      const _this = this;
      let select_text;

      if (_this.$target.is("select")) {
        select_text = $("option:selected", _this.$target).text().trim();
        _this._fakeSelectText(select_text);
      } else if (_this.$target.is("input") || _this.$target.is("textarea")) {
        const is_read_only = _this.$target.attr("readonly");
        const select_text = _this.$target.val().trim();

        if (!is_read_only) {
          _this.$target.prop("readonly", true);
        }

        if (_this.action === "copy") {
          _this._fakeSelectText(select_text);
        } else {
          _this.$target.get(0).select();
          _this.$target.get(0).setSelectionRange(0, select_text.length);
        }

        if (!is_read_only) {
          _this.$target.removeAttr("readonly");
        }
      }
    }

    _clearSelection () {
      const _this = this;

      document.activeElement.blur();
      window.getSelection().removeAllRanges();

      _this.$el.focus();

      if (_this.$dummy) {
        _this.$dummy.remove();
      }
    }

    _copyText () {
      const _this = this;

      document.execCommand(_this.action);
    }
  }

  $.fn[plugin_name] = initPlugin(clipBoardPlugin, plugin_name);
})(jQuery);


// #############################################################################
// TOASTER

/**
 * Initial:
 *
 * <a data-toaster="{% url "toaster" %}" data-toaster-text="Toaster text">Link</a>
 *
 * $("body").toaster({
 *  selector: "[data-toaster]",
 * });
 *
 * Update toaster:
 *
 * $("body").toaster("updateToaster", toaster_html);
 *
 * Save toaster:
 *
 * $("body").toaster("saveToaster", toaster_html);
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "toaster";

  const $defaults = {
    selector: "[data-toaster]",
  };

  class toasterPlugin {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.el = $element;

      this.$el = $($element);
      this.$wrapper = $("#toaster_wrapper");

      this.init();
    }

    init () {
      const _this = this;

      _this.$el.on("click", _this.$settings.selector, function () {
        const $this = $(this);
        const toaster = $this.data("toaster");

        $.ajax({
          data: {
            success: true,
            text: $this.data("toaster-text"),
          },
          type: "POST",
          url: toaster,
          success: function ($data) {
            _this.updateToaster($data.toaster);
          },
        });
      });

      _this._restoreToaster();
    }

    _restoreToaster () {
      const _this = this;
      const toaster = sessionStorage.getItem("toaster");

      if (toaster) {
        _this.updateToaster(toaster);
        sessionStorage.removeItem("toaster");
      }
    }

    saveToaster (toaster_html) {
      sessionStorage.setItem("toaster", toaster_html);
    }

    updateToaster (toaster_html) {
      const _this = this;
      _this.$wrapper.prepend(toaster_html);

      const $toast = $(".toast:not(.fade)", _this.$wrapper);
      $toast.toast("show");

      $toast.on("show.bs.toast", function () {
        $(this).toast("dispose");
      });
    }
  }

  $.fn[plugin_name] = initPlugin(toasterPlugin, plugin_name);
})(jQuery);


// #############################################################################
// AUTO UPDATE HTML CONTENT

/**
 * Initial:
 *
 * <div data-update-html-content="/UPDATE_URL/">
 *   Auto update content inside this div.
 * </div>
 *
 * UPDATE_URL is a JSON file like in updateHtmlContent()
 *
 * $("body").autoUpdateHtmlContent({
 *  selector: "[data-update-html-content]",
 * });
 *
 **/

(function ($) {
  "use strict";

  const plugin_name = "autoUpdateHtmlContent";

  const $defaults = {
    selector: "[data-update-html-content]",
    update_interval: 10000,
  };

  class autoUpdateHtmlContent {
    constructor ($element, $options) {
      this.$settings = $.extend({}, $defaults, $options);

      this.$el = $($element);
      this.$wrappers = $("[data-update-html-content]", $element);

      this.init();
    }

    init () {
      const _this = this;

      _this.$wrappers.each(function () {
        const url = this.getAttribute("data-update-html-content");

        if (url) {
          const $element = this;
          const interval_time = this.getAttribute("data-update-interval") || _this.$settings.update_interval;

          _this._update($element, url);

          _this.interval = setInterval(function () {
            _this._update($element, url);
          }, interval_time);
        }
      });
    }

    _update ($wrapper, url) {
      $.ajax({
        dataType: "json",
        url: url,
        success: function ($data) {
          updateHtmlContent($data, $wrapper);
        },
      });
    }
  }

  $.fn[plugin_name] = initPlugin(autoUpdateHtmlContent, plugin_name);
})(jQuery);
