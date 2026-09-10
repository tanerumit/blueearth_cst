# One Julia session amortizes Wflow load/JIT across an explicitly identified batch.
# Snakemake still owns batch-level output cleanup on failure; every failure row
# therefore names the batch and ALL affected runs, not just the failing member.
using Dates

function parse_batch(args)
    length(args) >= 4 && (length(args) - 1) % 3 == 0 ||
        error("Expected batch_id followed by (run_id, toml_path, native_output_path) records")
    batch_id = args[1]
    isempty(batch_id) && error("batch_id must be nonempty")
    members = [(run_id=args[i], toml_path=args[i+1], native_output_path=args[i+2])
               for i in 2:3:length(args)]
    ids = [member.run_id for member in members]
    all(id -> !isempty(id) && all(isdigit, id), ids) ||
        error("Batch run ids must be explicit numeric identifiers")
    length(unique(ids)) == length(ids) || error("Duplicate run id in batch")
    issorted(parse.(BigInt, ids)) || error("Batch run ids must be in increasing numeric order")
    outputs = [member.native_output_path for member in members]
    length(unique(outputs)) == length(outputs) || error("Duplicate native output in batch")
    return batch_id, members
end

# Kept outside the executable block so parser tests need neither Wflow nor a model.
row(body) = println("$(Dates.format(now(), "HH:MM:SS")) - wflow - $(body)")

if abspath(PROGRAM_FILE) == @__FILE__
    batch_id, members = parse_batch(ARGS)
    include(joinpath(@__DIR__, "..", "shared", "wflow_progress.jl"))
    using .WflowProgress: open_frame, run_with_progress, format_elapsed
    open_frame(first(members).run_id)
    using Wflow

    exitcode = 0
    total = length(members)
    affected = join([member.run_id for member in members], ",")
    for (k, member) in enumerate(members)
        global exitcode
        tag = member.run_id
        try
            dt = @elapsed run_with_progress(Wflow, member.toml_path; label=tag)
            isfile(member.native_output_path) ||
                error("Missing native output $(member.native_output_path)")
            row("[$(k)/$(total)] $(tag)  $(format_elapsed(dt))")
            flush(stdout)
        catch e
            row("FAILED [$(k)/$(total)] $(tag) batch=$(batch_id) runs=[$(affected)]  $(sprint(showerror, e))")
            flush(stdout)
            exitcode = 1
        end
    end
    exit(exitcode)
end
